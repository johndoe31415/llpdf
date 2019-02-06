#	bulkscan - Document scanning and maintenance solution
#	Copyright (C) 2019-2019 Johannes Bauer
#
#	This file is part of bulkscan.
#
#	bulkscan is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	bulkscan is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with bulkscan; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import subprocess
import enum
import json
from .NamedVector import NamedVector

class UnsupportedError(Exception): pass

class PixelFormat(enum.IntEnum):
	BlackWhite = 0
	Grayscale = 1
	RGB = 2

class Dimensions(NamedVector):
	_COMPONENTS = [ "width", "height" ]

class Margin(NamedVector):
	_COMPONENTS = [ "top", "right", "bottom", "left" ]

class ResolutionDPI(NamedVector):
	_COMPONENTS = [ "x", "y" ]

class PDFExtImage(object):
	def __init__(self, data, image_format, pixel_format, dimensions, resolution_dpi, comment = None):
		assert(isinstance(pixel_format, PixelFormat))
		self._data = data
		self._image_format = image_format.upper()
		self._pixel_format = pixel_format
		self._dimensions = dimensions
		self._resolution_dpi = resolution_dpi
		self._comment = comment

	@property
	def data(self):
		return self._data

	@property
	def image_format(self):
		return self._image_format

	@property
	def pixel_format(self):
		return self._pixel_format

	@property
	def dimensions(self):
		return self._dimensions

	@property
	def resolution_dpi(self):
		return self._resolution_dpi

	@property
	def comment(self):
		return self._comment

	@property
	def extents_mm(self):
		return Dimensions(width = self.dimensions.width / self._resolution_dpi.x * 25.4, height = self.dimensions.height / self._resolution_dpi.y * 25.4)

	def convert_to(self, image_format = None, pixel_format = None, resolution_dpi = None):
		cmd = [ "convert" ]

		# Change pixel format, if requested
		if pixel_format is not None:
			if pixel_format == PixelFormat.RGB:
				cmd += [ "-set", "colorspace", "sRGB", "-depth", "8", "-type", "truecolor" ]
			elif pixel_format == PixelFormat.Grayscale:
				cmd += [ "-set", "colorspace", "gray", "-depth", "8", "-type", "grayscale" ]
			elif pixel_format == PixelFormat.BlackWhite:
				if image_format == "JPEG":
					raise UnsupportedError("JPEG does not support pixel format BlackWhite.")
				cmd += [ "-set", "colorspace", "gray", "-type", "bilevel", "-depth", "1" ]
			else:
				raise NotImplementedError(pixel_format)
		else:
			pixel_format = self.pixel_format

		# Change resolution, if requested
		if resolution_dpi is not None:
			new_resolution = ResolutionDPI(resolution_dpi, resolution_dpi)
			new_dimensions = Dimensions(width = round(self.dimensions.width * new_resolution.x / self.resolution_dpi.x), height = round(self.dimensions.height * new_resolution.y / self.resolution_dpi.y))
			cmd += [ "-geometry", "%dx%d!" % (new_dimensions.width, new_dimensions.height), "-units", "PixelsPerInch", "-density", "%f" % (new_resolution.x) ]
		else:
			new_resolution = self.resolution_dpi
			new_dimensions = self.dimensions

		# Change format, if requested
		cmd += [ "-" ]
		if image_format is not None:
			cmd += [ image_format + ":-" ]
		else:
			cmd += [ self.image_format + ":-" ]
			image_format = self.image_format
#		print(" ".join(cmd))
		data = subprocess.check_output(cmd, input = self._data)
		return PDFExtImage(data = data, image_format = image_format, pixel_format = pixel_format, dimensions = new_dimensions, resolution_dpi = new_resolution, comment = self.comment)

	@classmethod
	def _identify_image(cls, image_data):
		field_defs = {
			"%w":				"width",
			"%h":				"height",
			"%x":				"resolution_x",
			"%y":				"resolution_y",
			"%U":				"resolution_unit",
			"%m":				"image_format",
			"%[bit-depth]":		"bit_depth",
			"%[colorspace]":	"color_space",
			"%c":				"comment",
		}
		field_defs = sorted((x, y) for (x, y) in field_defs.items())
		cmd = [ "identify", "-format", "\\n".join(field_def[0] for field_def in field_defs), "-" ]
		stdout = subprocess.check_output(cmd, input = image_data)
		field_values = stdout.decode("ascii").split("\n")
		fields = { key: value for (key, value) in zip((field_def[1] for field_def in field_defs), field_values) }
		resolution_factor = {
			"PixelsPerInch":		1,
			"PixelsPerCentimeter":	2.54,
		}[fields["resolution_unit"]]
		pixel_format = {
			("sRGB", 8):		PixelFormat.RGB,
			("Gray", 8):		PixelFormat.Grayscale,
		}[(fields["color_space"], int(fields["bit_depth"]))]
		result = {
			"dimensions":			Dimensions(int(fields["width"]), int(fields["height"])),
			"resolution_dpi":		ResolutionDPI(float(fields["resolution_x"]) * resolution_factor, float(fields["resolution_y"]) * resolution_factor),
			"image_format":			fields["image_format"],
			"pixel_format":			pixel_format,
			"comment":				fields["comment"],
		}
		return result

	@classmethod
	def from_data(cls, image_data):
		info = cls._identify_image(image_data)
		return cls(data = image_data, image_format = info["image_format"], pixel_format = info["pixel_format"], dimensions = info["dimensions"], resolution_dpi = info["resolution_dpi"], comment = info["comment"])

	@classmethod
	def from_file(cls, filename):
		with open(filename, "rb") as f:
			data = f.read()
		return cls.from_data(data)

	def __str__(self):
		return "PDFExtImage<%d bytes, %s, %s, %d x %dpx / %.1f x %.1fmm>" % (len(self._data), self.image_format, self.pixel_format, self.dimensions.width, self.dimensions.height, self.extents_mm.width, self.extents_mm.height)
