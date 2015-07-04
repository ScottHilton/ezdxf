# Purpose: work with true color values
# Created: 03.07.2015 taken from my dxfgrabber package
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
__author__ = 'mozman'

def int2rgb(value):
    return (
        (value >> 16) & 0xFF,  # red
        (value >> 8) & 0xFF,  # green
        value & 0xFF,  # blue
    )

def rgb2int(rgb):
    r, g, b = rgb
    return ((int(r) & 0xff) << 16) | ((int(g) & 0xff) << 8) | (int(b) & 0xff)

def aci2rgb(index):
        if index < 1:
            raise IndexError(index)
        return int2rgb(dxf_default_colors[index])


dxf_default_colors = [
    0x000000,
    0xff0000,
    0xffff00,
    0x00ff00,
    0x00ffff,
    0x0000ff,
    0xff00ff,
    0xffffff,
    0x414141,
    0x808080,
    0xff0000,
    0xffaaaa,
    0xbd0000,
    0xbd7e7e,
    0x810000,
    0x815656,
    0x680000,
    0x684545,
    0x4f0000,
    0x4f3535,
    0xff3f00,
    0xffbfaa,
    0xbd2e00,
    0xbd8d7e,
    0x811f00,
    0x816056,
    0x681900,
    0x684e45,
    0x4f1300,
    0x4f3b35,
    0xff7f00,
    0xffd4aa,
    0xbd5e00,
    0xbd9d7e,
    0x814000,
    0x816b56,
    0x683400,
    0x685645,
    0x4f2700,
    0x4f4235,
    0xffbf00,
    0xffeaaa,
    0xbd8d00,
    0xbdad7e,
    0x816000,
    0x817656,
    0x684e00,
    0x685f45,
    0x4f3b00,
    0x4f4935,
    0xffff00,
    0xffffaa,
    0xbdbd00,
    0xbdbd7e,
    0x818100,
    0x818156,
    0x686800,
    0x686845,
    0x4f4f00,
    0x4f4f35,
    0xbfff00,
    0xeaffaa,
    0x8dbd00,
    0xadbd7e,
    0x608100,
    0x768156,
    0x4e6800,
    0x5f6845,
    0x3b4f00,
    0x494f35,
    0x7fff00,
    0xd4ffaa,
    0x5ebd00,
    0x9dbd7e,
    0x408100,
    0x6b8156,
    0x346800,
    0x566845,
    0x274f00,
    0x424f35,
    0x3fff00,
    0xbfffaa,
    0x2ebd00,
    0x8dbd7e,
    0x1f8100,
    0x608156,
    0x196800,
    0x4e6845,
    0x134f00,
    0x3b4f35,
    0x00ff00,
    0xaaffaa,
    0x00bd00,
    0x7ebd7e,
    0x008100,
    0x568156,
    0x006800,
    0x456845,
    0x004f00,
    0x354f35,
    0x00ff3f,
    0xaaffbf,
    0x00bd2e,
    0x7ebd8d,
    0x00811f,
    0x568160,
    0x006819,
    0x45684e,
    0x004f13,
    0x354f3b,
    0x00ff7f,
    0xaaffd4,
    0x00bd5e,
    0x7ebd9d,
    0x008140,
    0x56816b,
    0x006834,
    0x456856,
    0x004f27,
    0x354f42,
    0x00ffbf,
    0xaaffea,
    0x00bd8d,
    0x7ebdad,
    0x008160,
    0x568176,
    0x00684e,
    0x45685f,
    0x004f3b,
    0x354f49,
    0x00ffff,
    0xaaffff,
    0x00bdbd,
    0x7ebdbd,
    0x008181,
    0x568181,
    0x006868,
    0x456868,
    0x004f4f,
    0x354f4f,
    0x00bfff,
    0xaaeaff,
    0x008dbd,
    0x7eadbd,
    0x006081,
    0x567681,
    0x004e68,
    0x455f68,
    0x003b4f,
    0x35494f,
    0x007fff,
    0xaad4ff,
    0x005ebd,
    0x7e9dbd,
    0x004081,
    0x566b81,
    0x003468,
    0x455668,
    0x00274f,
    0x35424f,
    0x003fff,
    0xaabfff,
    0x002ebd,
    0x7e8dbd,
    0x001f81,
    0x566081,
    0x001968,
    0x454e68,
    0x00134f,
    0x353b4f,
    0x0000ff,
    0xaaaaff,
    0x0000bd,
    0x7e7ebd,
    0x000081,
    0x565681,
    0x000068,
    0x454568,
    0x00004f,
    0x35354f,
    0x3f00ff,
    0xbfaaff,
    0x2e00bd,
    0x8d7ebd,
    0x1f0081,
    0x605681,
    0x190068,
    0x4e4568,
    0x13004f,
    0x3b354f,
    0x7f00ff,
    0xd4aaff,
    0x5e00bd,
    0x9d7ebd,
    0x400081,
    0x6b5681,
    0x340068,
    0x564568,
    0x27004f,
    0x42354f,
    0xbf00ff,
    0xeaaaff,
    0x8d00bd,
    0xad7ebd,
    0x600081,
    0x765681,
    0x4e0068,
    0x5f4568,
    0x3b004f,
    0x49354f,
    0xff00ff,
    0xffaaff,
    0xbd00bd,
    0xbd7ebd,
    0x810081,
    0x815681,
    0x680068,
    0x684568,
    0x4f004f,
    0x4f354f,
    0xff00bf,
    0xffaaea,
    0xbd008d,
    0xbd7ead,
    0x810060,
    0x815676,
    0x68004e,
    0x68455f,
    0x4f003b,
    0x4f3549,
    0xff007f,
    0xffaad4,
    0xbd005e,
    0xbd7e9d,
    0x810040,
    0x81566b,
    0x680034,
    0x684556,
    0x4f0027,
    0x4f3542,
    0xff003f,
    0xffaabf,
    0xbd002e,
    0xbd7e8d,
    0x81001f,
    0x815660,
    0x680019,
    0x68454e,
    0x4f0013,
    0x4f353b,
    0x333333,
    0x505050,
    0x696969,
    0x828282,
    0xbebebe,
    0xffffff,
]
