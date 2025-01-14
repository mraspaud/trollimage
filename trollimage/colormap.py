#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, 2013, 2014 Martin Raspaud

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""A simple colormap module.
"""

import numpy as np
from trollimage.colorspaces import rgb2hcl, hcl2rgb


def colorize(arr, colors, values):
    """Colorize a monochromatic array *arr*, based *colors* given for
    *values*. Interpolation is used. *values* must be in ascending order.
    """
    hcolors = np.array([rgb2hcl(*i[:3]) for i in colors])
    # unwrap colormap in hcl space
    hcolors[:, 0] = np.rad2deg(np.unwrap(np.deg2rad(np.array(hcolors)[:, 0])))
    channels = [np.interp(arr,
                          np.array(values),
                          np.array(hcolors)[:, i])
                for i in range(3)]

    channels = list(hcl2rgb(*channels))

    rest = [np.interp(arr,
                      np.array(values),
                      np.array(colors)[:, i + 3])
            for i in range(np.array(colors).shape[1] - 3)]

    channels.extend(rest)

    try:
        return [np.ma.array(channel, mask=arr.mask) for channel in channels]
    except AttributeError:
        return channels


def palettize(arr, colors, values):
    """From start *values* apply *colors* to *data*.
    """
    new_arr = np.digitize(arr.ravel(),
                          np.concatenate((values,
                                          [max(np.nanmax(arr),
                                               values.max()) + 1])))
    new_arr -= 1
    new_arr = new_arr.clip(min=0, max=len(values) - 1)
    try:
        new_arr = np.ma.array(new_arr.reshape(arr.shape), mask=arr.mask)
    except AttributeError:
        new_arr = new_arr.reshape(arr.shape)

    return new_arr, tuple(colors)


class Colormap(object):
    """The colormap object.

    Initialize with tuples of (value, (colors)), like this::

      Colormap((-75.0, (1.0, 1.0, 0.0)),
               (-40.0001, (0.0, 1.0, 1.0)),
               (-40.0, (1, 1, 1)),
               (30.0, (0, 0, 0)))


    You can also concatenate colormaps together, try::

      cm = cm1 + cm2

    """

    def __init__(self, *tuples, **kwargs):
        if 'colors' in kwargs and 'values' in kwargs:
            values = kwargs['values']
            colors = kwargs['colors']
        else:
            values = [a for (a, b) in tuples]
            colors = [b for (a, b) in tuples]
        self.values = np.array(values)
        self.colors = np.array(colors)

    def colorize(self, data):
        """Colorize a monochromatic array *data*, based on the current colormap.
        """
        return colorize(data,
                        self.colors,
                        self.values)

    def palettize(self, data):
        """Palettize a monochromatic array *data* based on the current colormap.
        """
        return palettize(data, self.colors, self.values)

    def __add__(self, other):
        new = Colormap()
        new.values = np.concatenate((self.values, other.values))
        new.colors = np.concatenate((self.colors, other.colors))
        return new

    def reverse(self):
        """Reverse the current colormap in place.
        """
        self.colors = np.flipud(self.colors)

    def set_range(self, min_val, max_val):
        """Set the range of the colormap to [*min_val*, *max_val*]
        """
        if min_val > max_val:
            max_val, min_val = min_val, max_val
        self.values = (((self.values * 1.0 - self.values.min()) /
                        (self.values.max() - self.values.min()))
                       * (max_val - min_val) + min_val)

    def to_rio(self):
        """Converts the colormap to a rasterio colormap.
        """
        self.colors = (((self.colors * 1.0 - self.colors.min()) /
                        (self.colors.max() - self.colors.min())) * 255)
        return dict(zip(self.values, tuple(map(tuple, self.colors))))


# matlab jet "#00007F", "blue", "#007FFF", "cyan", "#7FFF7F", "yellow",
# "#FF7F00", "red", "#7F0000"

rainbow = Colormap((0.000, (0.0, 0.0, 0.5)),
                   (0.125, (0.0, 0.0, 1.0)),
                   (0.250, (0.0, 0.5, 1.0)),
                   (0.375, (0.0, 1.0, 1.0)),
                   (0.500, (0.5, 1.0, 0.5)),
                   (0.625, (1.0, 1.0, 0.0)),
                   (0.750, (1.0, 0.5, 0.0)),
                   (0.875, (1.0, 0.0, 0.0)),
                   (1.000, (0.5, 0.0, 0.0)))

# * Colors from www.ColorBrewer.org by Cynthia A. Brewer, Geography,
# * Pennsylvania State University.

# * Single hue *

blues = Colormap((0.000, (247 / 255.0, 251 / 255.0, 1.0)),
                 (1.000, (8 / 255.0, 48 / 255.0, 107 / 255.0)))

greens = Colormap((0.000, (247 / 255.0, 252 / 255.0, 245 / 255.0)),
                  (1.000, (0.0, 68 / 255.0, 27 / 255.0)))

greys = Colormap((0.0, (1.0, 1.0, 1.0)),
                 (1.0, (0.0, 0.0, 0.0)))

oranges = Colormap((0.0, (1.0, 245 / 255.0, 235 / 255.0)),
                   (1.0, (127 / 255.0, 39 / 255.0, 4 / 255.0)))

purples = Colormap((0.0, (252 / 255.0, 251 / 255.0, 253 / 255.0)),
                   (1.0, (63 / 255.0, 0.0, 125 / 255.0)))

reds = Colormap((0.0, (1.0, 245 / 255.0, 240 / 255.0)),
                (1.0, (103 / 255.0, 0.0, 13 / 255.0)))

# * Multihue *

# BuGn

bugn = Colormap((0.000, (247 / 255.0, 252 / 255.0, 253 / 255.0)),
                (1.000, (0.0, 68 / 255.0, 27 / 255.0)))

# BuPu

bupu = Colormap((0.000, (247 / 255.0, 252 / 255.0, 253 / 255.0)),
                (1.000, (77 / 255.0, 0.0, 75 / 255.0)))

# GnBu

gnbu = Colormap((0.000, (247 / 255.0, 252 / 255.0, 240 / 255.0)),
                (1.000, (8 / 255.0, 64 / 255.0, 129 / 255.0)))

# OrRd

orrd = Colormap((0.000, (255 / 255.0, 247 / 255.0, 236 / 255.0)),
                (1.000, (127 / 255.0, 0.0, 0.0)))

# PuBu

pubu = Colormap((0.000, (1.0, 247 / 255.0, 251 / 255.0)),
                (0.500, (116 / 255.0, 169 / 255.0, 207 / 255.0)),
                (1.000, (2 / 255.0, 56 / 255.0, 88 / 255.0)))

# PuBuGn

pubugn = Colormap((0.000, (1.0, 247 / 255.0, 251 / 255.0)),
                  (0.500, (103 / 255.0, 169 / 255.0, 207 / 255.0)),
                  (1.000, (1 / 255.0, 70 / 255.0, 54 / 255.0)))

# PuRd

purd = Colormap((0.000, (247 / 255.0, 244 / 255.0, 249 / 255.0)),
                (1.000, (103 / 255.0, 0.0, 31 / 255.0)))

# RdPu

rdpu = Colormap((0.000, (1.0, 247 / 255.0, 243 / 255.0)),
                (1.000, (73 / 255.0, 0.0, 106 / 255.0)))

# YlGn

ylgn = Colormap((0.000, (1.0, 1.0, 229 / 255.0)),
                (1.000, (0.0, 69 / 255.0, 41 / 255.0)))

# YlGnBu

ylgnbu = Colormap((0.000, (1.0, 1.0, 217 / 255.0)),
                  (1.000, (8 / 255.0, 29 / 255.0, 88 / 255.0)))

# YlOrBr

ylorbr = Colormap((0.000, (1.0, 1.0, 229 / 255.0)),
                  (0.500, (254 / 255.0, 153 / 255.0, 41 / 255.0)),
                  (1.000, (102 / 255.0, 37 / 255.0, 6 / 255.0)))

# YlOrRd

ylorrd = Colormap((0.000, (1.0, 1.0, 204 / 255.0)),
                  (0.500, (254 / 255.0, 141 / 255.0, 60 / 255.0)),
                  (1.000, (128 / 255.0, 0.0, 38 / 255.0)))

sequential_colormaps = [blues, greens, greys, oranges, purples, reds,
                        bugn, bupu, gnbu, orrd, pubu, pubugn, purd, rdpu,
                        ylgn, ylgnbu, ylorbr, ylorrd]

# * Diverging *

brbg = Colormap((0.0, (84 / 255.0, 48 / 255.0, 5 / 255.0)),
                (0.1, (140 / 255.0, 81 / 255.0, 10 / 255.0)),
                (0.2, (191 / 255.0, 129 / 255.0, 45 / 255.0)),
                (0.3, (223 / 255.0, 129 / 255.0, 125 / 255.0)),
                (0.4, (246 / 255.0, 232 / 255.0, 195 / 255.0)),
                (0.5, (245 / 255.0, 245 / 255.0, 245 / 255.0)),
                (0.6, (199 / 255.0, 234 / 255.0, 229 / 255.0)),
                (0.7, (128 / 255.0, 205 / 255.0, 193 / 255.0)),
                (0.8, (53 / 255.0, 151 / 255.0, 143 / 255.0)),
                (0.9, (1 / 255.0, 102 / 255.0, 94 / 255.0)),
                (1.0, (0 / 255.0, 60 / 255.0, 48 / 255.0)))

piyg = Colormap((0.0, (142 / 255.0, 1 / 255.0, 82 / 255.0)),
                (0.1, (197 / 255.0, 27 / 255.0, 125 / 255.0)),
                (0.2, (222 / 255.0, 119 / 255.0, 174 / 255.0)),
                (0.3, (241 / 255.0, 182 / 255.0, 218 / 255.0)),
                (0.4, (253 / 255.0, 224 / 255.0, 239 / 255.0)),
                (0.5, (247 / 255.0, 247 / 255.0, 247 / 255.0)),
                (0.6, (230 / 255.0, 245 / 255.0, 208 / 255.0)),
                (0.7, (184 / 255.0, 225 / 255.0, 134 / 255.0)),
                (0.8, (127 / 255.0, 188 / 255.0, 65 / 255.0)),
                (0.9, (77 / 255.0, 146 / 255.0, 33 / 255.0)),
                (1.0, (39 / 255.0, 100 / 255.0, 25 / 255.0)))

prgn = Colormap((0.0, (64 / 255.0, 0 / 255.0, 75 / 255.0)),
                (0.1, (118 / 255.0, 42 / 255.0, 131 / 255.0)),
                (0.2, (153 / 255.0, 112 / 255.0, 171 / 255.0)),
                (0.3, (194 / 255.0, 165 / 255.0, 207 / 255.0)),
                (0.4, (231 / 255.0, 212 / 255.0, 232 / 255.0)),
                (0.5, (247 / 255.0, 247 / 255.0, 247 / 255.0)),
                (0.6, (217 / 255.0, 240 / 255.0, 211 / 255.0)),
                (0.7, (166 / 255.0, 219 / 255.0, 160 / 255.0)),
                (0.8, (90 / 255.0, 174 / 255.0, 97 / 255.0)),
                (0.9, (27 / 255.0, 120 / 255.0, 55 / 255.0)),
                (1.0, (0 / 255.0, 68 / 255.0, 27 / 255.0)))

puor = Colormap((0.0, (127 / 255.0, 59 / 255.0, 8 / 255.0)),
                (0.1, (179 / 255.0, 88 / 255.0, 6 / 255.0)),
                (0.2, (224 / 255.0, 130 / 255.0, 20 / 255.0)),
                (0.3, (253 / 255.0, 184 / 255.0, 99 / 255.0)),
                (0.4, (254 / 255.0, 224 / 255.0, 182 / 255.0)),
                (0.5, (247 / 255.0, 247 / 255.0, 247 / 255.0)),
                (0.6, (216 / 255.0, 218 / 255.0, 235 / 255.0)),
                (0.7, (178 / 255.0, 171 / 255.0, 210 / 255.0)),
                (0.8, (128 / 255.0, 115 / 255.0, 172 / 255.0)),
                (0.9, (84 / 255.0, 39 / 255.0, 136 / 255.0)),
                (1.0, (45 / 255.0, 0 / 255.0, 75 / 255.0)))

rdbu = Colormap((0.0, (103 / 255.0, 0 / 255.0, 31 / 255.0)),
                (0.1, (178 / 255.0, 24 / 255.0, 43 / 255.0)),
                (0.2, (214 / 255.0, 96 / 255.0, 77 / 255.0)),
                (0.3, (244 / 255.0, 165 / 255.0, 130 / 255.0)),
                (0.4, (253 / 255.0, 219 / 255.0, 199 / 255.0)),
                (0.5, (247 / 255.0, 247 / 255.0, 247 / 255.0)),
                (0.6, (209 / 255.0, 229 / 255.0, 240 / 255.0)),
                (0.7, (146 / 255.0, 197 / 255.0, 222 / 255.0)),
                (0.8, (67 / 255.0, 147 / 255.0, 195 / 255.0)),
                (0.9, (33 / 255.0, 102 / 255.0, 172 / 255.0)),
                (1.0, (5 / 255.0, 48 / 255.0, 97 / 255.0)))

rdgy = Colormap((0.0, (103 / 255.0, 0 / 255.0, 31 / 255.0)),
                (0.1, (178 / 255.0, 24 / 255.0, 43 / 255.0)),
                (0.2, (214 / 255.0, 96 / 255.0, 77 / 255.0)),
                (0.3, (244 / 255.0, 165 / 255.0, 130 / 255.0)),
                (0.4, (253 / 255.0, 219 / 255.0, 199 / 255.0)),
                (0.5, (255 / 255.0, 255 / 255.0, 255 / 255.0)),
                (0.6, (224 / 255.0, 224 / 255.0, 224 / 255.0)),
                (0.7, (186 / 255.0, 186 / 255.0, 186 / 255.0)),
                (0.8, (135 / 255.0, 135 / 255.0, 135 / 255.0)),
                (0.9, (77 / 255.0, 77 / 255.0, 77 / 255.0)),
                (1.0, (26 / 255.0, 26 / 255.0, 26 / 255.0)))

rdylbu = Colormap((0.0, (165 / 255.0, 0 / 255.0, 38 / 255.0)),
                  (0.1, (215 / 255.0, 48 / 255.0, 39 / 255.0)),
                  (0.2, (244 / 255.0, 109 / 255.0, 67 / 255.0)),
                  (0.3, (253 / 255.0, 174 / 255.0, 97 / 255.0)),
                  (0.4, (254 / 255.0, 224 / 255.0, 144 / 255.0)),
                  (0.5, (255 / 255.0, 255 / 255.0, 191 / 255.0)),
                  (0.6, (224 / 255.0, 243 / 255.0, 248 / 255.0)),
                  (0.7, (171 / 255.0, 217 / 255.0, 233 / 255.0)),
                  (0.8, (116 / 255.0, 173 / 255.0, 209 / 255.0)),
                  (0.9, (69 / 255.0, 117 / 255.0, 180 / 255.0)),
                  (1.0, (49 / 255.0, 54 / 255.0, 149 / 255.0)))

rdylgn = Colormap((0.0, (165 / 255.0, 0 / 255.0, 38 / 255.0)),
                  (0.1, (215 / 255.0, 48 / 255.0, 39 / 255.0)),
                  (0.2, (244 / 255.0, 109 / 255.0, 67 / 255.0)),
                  (0.3, (253 / 255.0, 174 / 255.0, 97 / 255.0)),
                  (0.4, (254 / 255.0, 224 / 255.0, 139 / 255.0)),
                  (0.5, (255 / 255.0, 255 / 255.0, 191 / 255.0)),
                  (0.6, (217 / 255.0, 239 / 255.0, 139 / 255.0)),
                  (0.7, (166 / 255.0, 217 / 255.0, 106 / 255.0)),
                  (0.8, (102 / 255.0, 189 / 255.0, 99 / 255.0)),
                  (0.9, (26 / 255.0, 152 / 255.0, 80 / 255.0)),
                  (1.0, (0 / 255.0, 104 / 255.0, 55 / 255.0)))

spectral = Colormap((0.0, (158 / 255.0, 1 / 255.0, 66 / 255.0)),
                    (0.1, (213 / 255.0, 62 / 255.0, 79 / 255.0)),
                    (0.2, (244 / 255.0, 109 / 255.0, 67 / 255.0)),
                    (0.3, (253 / 255.0, 174 / 255.0, 97 / 255.0)),
                    (0.4, (254 / 255.0, 224 / 255.0, 139 / 255.0)),
                    (0.5, (255 / 255.0, 255 / 255.0, 191 / 255.0)),
                    (0.6, (230 / 255.0, 245 / 255.0, 152 / 255.0)),
                    (0.7, (171 / 255.0, 221 / 255.0, 164 / 255.0)),
                    (0.8, (102 / 255.0, 194 / 255.0, 165 / 255.0)),
                    (0.9, (50 / 255.0, 136 / 255.0, 189 / 255.0)),
                    (1.0, (94 / 255.0, 79 / 255.0, 162 / 255.0)))

diverging_colormaps = [brbg, piyg, prgn, puor, rdbu, rdgy, rdylbu, rdylgn,
                       spectral]

# * qualitative colormaps *

set1 = Colormap((0, (228 / 255.0, 26 / 255.0, 28 / 255.0)),
                (1, (55 / 255.0, 126 / 255.0, 184 / 255.0)),
                (2, (77 / 255.0, 175 / 255.0, 74 / 255.0)),
                (3, (152 / 255.0, 78 / 255.0, 163 / 255.0)),
                (4, (255 / 255.0, 127 / 255.0, 0 / 255.0)),
                (5, (255 / 255.0, 255 / 255.0, 51 / 255.0)),
                (6, (166 / 255.0, 86 / 255.0, 40 / 255.0)),
                (7, (247 / 255.0, 129 / 255.0, 191 / 255.0)),
                (8, (153 / 255.0, 153 / 255.0, 153 / 255.0)))

set2 = Colormap((0, (102 / 255.0, 194 / 255.0, 165 / 255.0)),
                (1, (252 / 255.0, 141 / 255.0, 98 / 255.0)),
                (2, (141 / 255.0, 160 / 255.0, 203 / 255.0)),
                (3, (231 / 255.0, 138 / 255.0, 195 / 255.0)),
                (4, (166 / 255.0, 216 / 255.0, 84 / 255.0)),
                (5, (255 / 255.0, 217 / 255.0, 47 / 255.0)),
                (6, (229 / 255.0, 196 / 255.0, 148 / 255.0)),
                (7, (179 / 255.0, 179 / 255.0, 179 / 255.0)))

set3 = Colormap((0, (141 / 255.0, 211 / 255.0, 199 / 255.0)),
                (1, (255 / 255.0, 255 / 255.0, 179 / 255.0)),
                (2, (190 / 255.0, 186 / 255.0, 218 / 255.0)),
                (3, (251 / 255.0, 128 / 255.0, 114 / 255.0)),
                (4, (128 / 255.0, 177 / 255.0, 211 / 255.0)),
                (5, (253 / 255.0, 180 / 255.0, 98 / 255.0)),
                (6, (179 / 255.0, 222 / 255.0, 105 / 255.0)),
                (7, (252 / 255.0, 205 / 255.0, 229 / 255.0)),
                (8, (217 / 255.0, 217 / 255.0, 217 / 255.0)),
                (9, (188 / 255.0, 128 / 255.0, 189 / 255.0)),
                (10, (204 / 255.0, 235 / 255.0, 197 / 255.0)),
                (11, (255 / 255.0, 237 / 255.0, 111 / 255.0)))

paired = Colormap((0, (166 / 255.0, 206 / 255.0, 227 / 255.0)),
                  (1, (31 / 255.0, 120 / 255.0, 180 / 255.0)),
                  (2, (178 / 255.0, 223 / 255.0, 138 / 255.0)),
                  (3, (51 / 255.0, 160 / 255.0, 44 / 255.0)),
                  (4, (251 / 255.0, 154 / 255.0, 153 / 255.0)),
                  (5, (227 / 255.0, 26 / 255.0, 28 / 255.0)),
                  (6, (253 / 255.0, 191 / 255.0, 111 / 255.0)),
                  (7, (255 / 255.0, 127 / 255.0, 0 / 255.0)),
                  (8, (202 / 255.0, 178 / 255.0, 214 / 255.0)),
                  (9, (106 / 255.0, 61 / 255.0, 154 / 255.0)),
                  (10, (255 / 255.0, 255 / 255.0, 153 / 255.0)),
                  (11, (177 / 255.0, 89 / 255.0, 40 / 255.0)))

accent = Colormap((0, (127 / 255.0, 201 / 255.0, 127 / 255.0)),
                  (1, (190 / 255.0, 174 / 255.0, 212 / 255.0)),
                  (2, (253 / 255.0, 192 / 255.0, 134 / 255.0)),
                  (3, (255 / 255.0, 255 / 255.0, 153 / 255.0)),
                  (4, (56 / 255.0, 108 / 255.0, 176 / 255.0)),
                  (5, (240 / 255.0, 2 / 255.0, 127 / 255.0)),
                  (6, (191 / 255.0, 91 / 255.0, 23 / 255.0)),
                  (7, (102 / 255.0, 102 / 255.0, 102 / 255.0)))

dark2 = Colormap((0, (27 / 255.0, 158 / 255.0, 119 / 255.0)),
                 (1, (217 / 255.0, 95 / 255.0, 2 / 255.0)),
                 (2, (117 / 255.0, 112 / 255.0, 179 / 255.0)),
                 (3, (231 / 255.0, 41 / 255.0, 138 / 255.0)),
                 (4, (102 / 255.0, 166 / 255.0, 30 / 255.0)),
                 (5, (230 / 255.0, 171 / 255.0, 2 / 255.0)),
                 (6, (166 / 255.0, 118 / 255.0, 29 / 255.0)),
                 (7, (102 / 255.0, 102 / 255.0, 102 / 255.0)))

pastel1 = Colormap((0, (251 / 255.0, 180 / 255.0, 174 / 255.0)),
                   (1, (179 / 255.0, 205 / 255.0, 227 / 255.0)),
                   (2, (204 / 255.0, 235 / 255.0, 197 / 255.0)),
                   (3, (222 / 255.0, 203 / 255.0, 228 / 255.0)),
                   (4, (254 / 255.0, 217 / 255.0, 166 / 255.0)),
                   (5, (255 / 255.0, 255 / 255.0, 204 / 255.0)),
                   (6, (229 / 255.0, 216 / 255.0, 189 / 255.0)),
                   (7, (253 / 255.0, 218 / 255.0, 236 / 255.0)),
                   (8, (242 / 255.0, 242 / 255.0, 242 / 255.0)))

pastel2 = Colormap((0, (179 / 255.0, 226 / 255.0, 205 / 255.0)),
                   (1, (253 / 255.0, 205 / 255.0, 172 / 255.0)),
                   (2, (203 / 255.0, 213 / 255.0, 232 / 255.0)),
                   (3, (244 / 255.0, 202 / 255.0, 228 / 255.0)),
                   (4, (230 / 255.0, 245 / 255.0, 201 / 255.0)),
                   (5, (255 / 255.0, 242 / 255.0, 174 / 255.0)),
                   (6, (241 / 255.0, 226 / 255.0, 204 / 255.0)),
                   (7, (204 / 255.0, 204 / 255.0, 204 / 255.0)))

qualitative_colormaps = [set1, set2, set3,
                         paired, accent, dark2,
                         pastel1, pastel2]


def colorbar(height, length, colormap):
    """Return the channels of a colorbar.
    """
    cbar = np.tile(np.arange(length) * 1.0 / (length - 1), (height, 1))
    cbar = (cbar * (colormap.values.max() - colormap.values.min())
            + colormap.values.min())

    return colormap.colorize(cbar)


def palettebar(height, length, colormap):
    """Return the channels of a palettebar.
    """
    cbar = np.tile(np.arange(length) * 1.0 / (length - 1), (height, 1))
    cbar = (cbar * (colormap.values.max() + 1 - colormap.values.min())
            + colormap.values.min())

    return colormap.palettize(cbar)
