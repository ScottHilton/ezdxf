# Created: 28.12.2018
# Copyright (C) 2018-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
from ezdxf.math import Vector, Vec2
from ezdxf.math import UCS
from ezdxf.tools import normalize_text_angle
from ezdxf.render.arrows import ARROWS, connection_point
from ezdxf.entities.dimstyleoverride import DimStyleOverride

from .dim_base import BaseDimensionRenderer, TextBox

if TYPE_CHECKING:
    from ezdxf.eztypes import Dimension, Vertex, GenericLayoutType


class RadiusDimension(BaseDimensionRenderer):
    """
    Radial dimension line renderer.

    Supported render types:
    - default location inside, text aligned with radial dimension line
    - default location inside horizontal text
    - default location outside, text aligned with radial dimension line
    - default location outside horizontal text
    - user defined location, text aligned with radial dimension line
    - user defined location horizontal text

    Args:
        dimension: DXF entity DIMENSION
        ucs: user defined coordinate system
        override: dimension style override management object

    """

    def __init__(self, dimension: 'Dimension', ucs: 'UCS' = None, override: 'DimStyleOverride' = None):
        super().__init__(dimension, ucs, override)
        self.center = Vec2(self.dimension.dxf.defpoint)
        self.point_on_circle = Vec2(self.dimension.dxf.defpoint4)
        # modify parameters for special scenarios
        if self.user_location is None:  # default location
            if self.text_inside and self.text_inside_horizontal and self.text_movement_rule == 1:  # move text, add leader
                # use algorithm for user define dimension line location
                self.user_location = self.center.lerp(self.point_on_circle)
                self.text_valign = 0  # text vertical centered

        direction = self.point_on_circle - self.center
        self.dim_line_vec = direction.normalize()
        self.dim_line_angle = self.dim_line_vec.angle_deg
        self.measurement = direction.magnitude
        self.outside_default_distance = self.measurement + 2 * self.arrow_size
        self.outside_default_defpoint = self.center + (self.dim_line_vec * self.outside_default_distance)
        self.outside_text_force_dimline = self.dim_style.get('dimtofl', 1)
        # final dimension text (without limits or tolerance)
        self.text = self.text_override(self.measurement * self.dim_measurement_factor)  # type: str

        # default location is outside, if not forced to be inside
        self.text_outside = not self.force_text_inside
        # text_outside: user defined location, overrides default location
        if self.user_location is not None:
            self.text_outside = self.is_location_outside(self.user_location)

        if self.text:
            # text width and required space
            self.dim_text_width = self.text_width(self.text)  # type: float
            if self.dim_tolerance:
                self.dim_text_width += self.tol_text_width

            elif self.dim_limits:
                # limits show the upper and lower limit of the measurement as stacked values
                # and with the size of tolerances
                measurement = self.measurement * self.dim_measurement_factor
                self.measurement_upper_limit = measurement + self.tol_maximum
                self.measurement_lower_limit = measurement - self.tol_minimum
                self.tol_text_upper = self.format_tolerance_text(self.measurement_upper_limit)
                self.tol_text_lower = self.format_tolerance_text(self.measurement_lower_limit)
                self.tol_text_width = self.tolerance_text_width(max(len(self.tol_text_upper), len(self.tol_text_lower)))

                # only limits are displayed so:
                self.dim_text_width = self.tol_text_width

        # default rotation is angle of dimension line, from center to point on circle.
        rotation = self.dim_line_angle
        if self.text_outside and self.text_outside_horizontal:
            rotation = 0
        elif self.text_inside and self.text_inside_horizontal:
            rotation = 0

        # final absolute text rotation (x-axis=0)
        self.text_rotation = normalize_text_angle(rotation, fix_upside_down=True)

        # final text location
        self.text_location = self.get_text_location()  # type: Vec2

        self.text_box = TextBox(
            center=self.text_location,
            width=self.dim_text_width,
            height=self.text_height,
            angle=self.text_rotation,
            gap=self.text_gap * .75
        )
        # write final text location into DIMENSION entity
        if self.user_location:
            self.dimension.dxf.text_midpoint = self.user_location
        # default locations
        elif self.text_outside and self.text_outside_horizontal:
            self.dimension.dxf.text_midpoint = self.outside_default_defpoint
        else:
            self.dimension.dxf.text_midpoint = self.text_location

    def text_override(self, measurement: float) -> str:
        """ Get measurement text, respect text suppression and insert prefix 'R' """
        text = super().text_override(measurement)
        if text and text[0] != 'R':
            text = 'R' + text
        return text

    def get_text_location(self) -> Vec2:
        """ Returns text midpoint from user defined location or default text location. """
        if self.user_location is not None:
            return self.get_user_defined_text_location()
        else:
            return self.get_default_text_location()

    def get_default_text_location(self) -> Vec2:
        """ Returns default text midpoint based on `self.text_valign` and `self.text_outside` """
        if self.text_outside and self.text_outside_horizontal:
            hdist = self.dim_text_width / 2.
            if self.vertical_placement == 0:  # shift text horizontal if vertical centered
                hdist += self.arrow_size
            angle = self.dim_line_angle % 360.  # normalize 0 .. 360
            if 90 < angle <= 270:
                hdist = -hdist
            return self.outside_default_defpoint + Vec2((hdist, self.text_vertical_distance()))

        text_direction = Vec2.from_deg_angle(self.text_rotation)
        vertical_direction = text_direction.orthogonal(ccw=True)
        vertical_distance = self.text_vertical_distance()
        if self.text_inside:
            hdist = (self.measurement - self.arrow_size) / 2
            text_midpoint = self.center + (self.dim_line_vec * hdist)
        else:
            hdist = self.dim_text_width / 2. + self.arrow_size + self.text_gap
            text_midpoint = self.point_on_circle + (self.dim_line_vec * hdist)
        return text_midpoint + (vertical_direction * vertical_distance)

    def get_user_defined_text_location(self) -> Vec2:
        """ Returns text midpoint for user defined dimension location. """
        text_outside_horiz = self.text_outside and self.text_outside_horizontal
        text_inside_horiz = self.text_inside and self.text_inside_horizontal
        if text_outside_horiz or text_inside_horiz:
            hdist = self.dim_text_width / 2
            if self.vertical_placement == 0:  # shift text horizontal if vertical centered
                hdist += self.arrow_size
            if self.user_location.x <= self.point_on_circle.x:
                hdist = -hdist
            vdist = self.text_vertical_distance()
            return self.user_location + Vec2((hdist, vdist))
        else:
            text_normal_vec = Vec2.from_deg_angle(self.text_rotation).orthogonal()
            return self.user_location + text_normal_vec * self.text_vertical_distance()

    def is_location_outside(self, location: Vec2) -> bool:
        radius = (location - self.center).magnitude
        return radius > self.measurement

    def render(self, block: 'GenericLayoutType') -> None:
        """ Create dimension geometry of basic DXF entities in the associated BLOCK layout. """
        # call required to setup some requirements
        super().render(block)
        if not self.suppress_dim1_line:
            if self.user_location is not None:
                self.render_user_location()
            else:
                self.render_default_location()

        # add measurement text as last entity to see text fill properly
        if self.text:
            if self.supports_dxf_r2000:
                text = self.compile_mtext()
            else:
                text = self.text
            self.add_measurement_text(text, self.text_location, self.text_rotation)

        # add POINT entities at definition points
        self.add_defpoints([self.center, self.point_on_circle])

    def render_default_location(self) -> None:
        """ Create dimension geometry at the default dimension line locations. """
        if not self.suppress_arrow1:
            arrow_connection_point = self.add_arrow()
        else:
            arrow_connection_point = self.point_on_circle

        if self.text_outside:
            if self.outside_text_force_dimline:
                self.add_radial_dim_line(self.point_on_circle)
            else:
                self.add_center_mark()
            if self.text_outside_horizontal:
                self.add_horiz_ext_line_default(arrow_connection_point)
            else:
                self.add_radial_ext_line_default(arrow_connection_point)
        else:
            if self.text_movement_rule == 1:
                # move text, add leader -> dimline from text to point on circle
                self.add_radial_dim_line_from_text(self.center.lerp(self.point_on_circle), arrow_connection_point)
                self.add_center_mark()
            else:
                # dimline from center to point on circle
                self.add_radial_dim_line(arrow_connection_point)

    def render_user_location(self) -> None:
        """ Create dimension geometry at user defined dimension locations. """
        preserve_outside = self.text_outside
        leader = self.text_movement_rule != 2
        if not leader:
            self.text_outside = False  # render dimension line like text inside
        # add arrow symbol (block references)
        if not self.suppress_arrow1:
            arrow_connection_point = self.add_arrow()
        else:
            arrow_connection_point = self.point_on_circle
        if self.text_outside:
            if self.outside_text_force_dimline:
                self.add_radial_dim_line(self.point_on_circle)
            else:
                self.add_center_mark()
            if self.text_outside_horizontal:
                self.add_horiz_ext_line_user(arrow_connection_point)
            else:
                self.add_radial_ext_line_user(arrow_connection_point)
        else:
            if self.text_inside_horizontal:
                self.add_horiz_ext_line_user(arrow_connection_point)
            else:
                if self.text_movement_rule == 2:  # move text, no leader!
                    # dimline from center to point on circle
                    self.add_radial_dim_line(arrow_connection_point)
                else:
                    # move text, add leader -> dimline from text to point on circle
                    self.add_radial_dim_line_from_text(self.user_location, arrow_connection_point)
                    self.add_center_mark()

        self.text_outside = preserve_outside

    def add_arrow(self) -> Vec2:
        """ Add arrow or tick to dimension line, returns dimension line connection point. """
        attribs = {
            'color': self.dim_line_color,
        }
        arrow_name = self.arrow1_name
        location = self.point_on_circle
        outside = self.text_outside
        if self.tick_size > 0.:  # oblique stroke, but double the size
            self.add_blockref(
                ARROWS.oblique,
                insert=location,
                rotation=self.dim_line_angle,
                scale=self.tick_size * 2,
                dxfattribs=attribs,
            )
        else:
            scale = self.arrow_size
            angle = self.dim_line_angle
            if outside:
                angle += 180

            self.add_blockref(arrow_name, insert=location, scale=scale, rotation=angle, dxfattribs=attribs)
            location = connection_point(arrow_name, location, scale, angle)
        return location

    def add_radial_dim_line(self, end: 'Vertex') -> None:
        """  Add radial dimension line. """
        attribs = self.dim_line_attributes()
        self.add_line(self.center, end, dxfattribs=attribs, remove_hidden_lines=True)

    def add_radial_dim_line_from_text(self, start, end: 'Vertex') -> None:
        """  Add radial dimension line, starting point at the measurement text. """
        attribs = self.dim_line_attributes()
        hshift = self.dim_text_width / 2
        if self.vertical_placement != 0:  # not center
            hshift = -hshift
        self.add_line(start + self.dim_line_vec * hshift, end, dxfattribs=attribs, remove_hidden_lines=False)

    def add_horiz_ext_line_default(self, start: 'Vertex') -> None:
        """ Add horizontal outside extension line from start for default locations. """
        attribs = self.dim_line_attributes()
        self.add_line(start, self.outside_default_defpoint, dxfattribs=attribs)
        if self.vertical_placement == 0:
            hdist = self.arrow_size
        else:
            hdist = self.dim_text_width
        angle = self.dim_line_angle % 360.  # normalize 0 .. 360
        if 90 < angle <= 270:
            hdist = -hdist
        end = self.outside_default_defpoint + Vec2((hdist, 0))
        self.add_line(self.outside_default_defpoint, end, dxfattribs=attribs)

    def add_horiz_ext_line_user(self, start: 'Vertex') -> None:
        """ Add horizontal extension line from start for user defined locations. """
        attribs = self.dim_line_attributes()
        self.add_line(start, self.user_location, dxfattribs=attribs)
        if self.vertical_placement == 0:
            hdist = self.arrow_size
        else:
            hdist = self.dim_text_width
        if self.user_location.x <= self.point_on_circle.x:
            hdist = -hdist
        end = self.user_location + Vec2((hdist, 0))
        self.add_line(self.user_location, end, dxfattribs=attribs)

    def add_radial_ext_line_default(self, start: 'Vertex') -> None:
        """ Add radial outside extension line from start for default locations. """
        attribs = self.dim_line_attributes()
        length = self.text_gap + self.dim_text_width
        end = start + self.dim_line_vec * length
        self.add_line(start, end, dxfattribs=attribs, remove_hidden_lines=True)

    def add_radial_ext_line_user(self, start: 'Vertex') -> None:
        """ Add radial outside extension line from start for user defined location. """
        attribs = self.dim_line_attributes()
        length = self.dim_text_width / 2
        if self.vertical_placement == 0:
            length = -length
        end = self.user_location + self.dim_line_vec * length
        self.add_line(start, end, dxfattribs=attribs)

    def add_measurement_text(self, dim_text: str, pos: Vec2, rotation: float) -> None:
        """ Add measurement text to dimension BLOCK. """
        attribs = {
            'color': self.text_color,
        }
        self.add_text(dim_text, pos=Vector(pos), rotation=rotation, dxfattribs=attribs)

    def add_center_mark(self):
        mark_size = self.dim_style.get('dimcen', 0)
        if mark_size == 0:
            return
        center = self.center
        if mark_size > 0:  # draw mark
            mark_x_vec = Vec2((mark_size, 0))
            mark_y_vec = Vec2((0, mark_size))
        else:  # draw line
            mark_size = -mark_size + self.measurement
            mark_x_vec = Vec2((mark_size, 0))
            mark_y_vec = Vec2((0, mark_size))

        self.add_line(center - mark_x_vec, center + mark_x_vec)
        self.add_line(center - mark_y_vec, center + mark_y_vec)

    def transform_ucs_to_wcs(self) -> None:
        """
        Transforms dimension definition points into WCS or if required into OCS.

        Can not be called in __init__(), because inherited classes may be need unmodified values.

        """

        def from_ucs(attr, func):
            point = self.dimension.get_dxf_attrib(attr)
            self.dimension.set_dxf_attrib(attr, func(point))

        from_ucs('defpoint', self.wcs)
        from_ucs('defpoint4', self.wcs)
        from_ucs('text_midpoint', self.ocs)


