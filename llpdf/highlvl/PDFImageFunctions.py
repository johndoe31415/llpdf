#	llpdf - Low-level PDF library in native Python.
#	Copyright (C) 2016-2019 Johannes Bauer
#
#	This file is part of llpdf.
#
#	llpdf is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	llpdf is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with llpdf; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>
#

import json
import zlib
import textwrap
from llpdf import PDFName, PDFString
from llpdf.img.PDFExtImage import PixelFormat, Margin
from llpdf.EncodeDecode import Filter, EncodedObject
from llpdf.img.PDFExtImage import Dimensions

class HighlevelPDFImageFunctions(object):
	def __init__(self, hl_page, margin = Margin(10, 10, 10, 10)):
		self._hl_page = hl_page
		self._margin = margin

	@property
	def pdf(self):
		return self._hl_page.pdf

	@property
	def printable_area_mm(self):
		page_extents = self._hl_page.extents_mm
		return Dimensions(width = page_extents.width - self._margin.left - self._margin.right, height = page_extents.height - self._margin.top - self._margin.bottom)

	def put_image(self, pdfimage):
		if pdfimage.image_format not in [ "JPEG", "RGB", "GRAY" ]:
			raise UnsupportedError("PDF can only handle JPEG, RGB or GRAY image formats, but %s was supplied." % (pdfimage.image_format))

		custom_metadata = {
			"resolution_dpi":	list(pdfimage.resolution_dpi),
			"comment":			pdfimage.comment,
		}
		image = self.pdf.new_object({
			PDFName("/Type"):				PDFName("/XObject"),
			PDFName("/Subtype"):			PDFName("/Image"),
			PDFName("/Interpolate"):		True,
			PDFName("/Width"):				pdfimage.dimensions.width,
			PDFName("/Height"):				pdfimage.dimensions.height,
			PDFName("/CustomMetadata"):		PDFString(json.dumps(custom_metadata)),
		})
		if pdfimage.image_format == "JPEG":
			image.set_stream(EncodedObject(encoded_data = pdfimage.data, filtering = Filter.DCTDecode))
		elif pdfimage.image_format in [ "RGB", "GRAY" ]:
			image.set_stream(EncodedObject.create(pdfimage.data, compress = True))
		else:
			raise NotImplementedError(pdfimage.image_format)

		if pdfimage.pixel_format == PixelFormat.RGB:
			image.content[PDFName("/ColorSpace")] = PDFName("/DeviceRGB")
			image.content[PDFName("/BitsPerComponent")] = 8
		elif pdfimage.pixel_format == PixelFormat.Grayscale:
			image.content[PDFName("/ColorSpace")] = PDFName("/DeviceGray")
			image.content[PDFName("/BitsPerComponent")] = 8
		elif pdfimage.pixel_format == PixelFormat.BlackWhite:
			image.content[PDFName("/ColorSpace")] = PDFName("/DeviceGray")
			image.content[PDFName("/BitsPerComponent")] = 1
		else:
			raise NotImplementedError(pdfimage.pixel_format)

		image_extents_mm = pdfimage.extents_mm
		image_scale_x = self.printable_area_mm.width / image_extents_mm.width
		image_scale_y = self.printable_area_mm.height / image_extents_mm.height
		image_scalar = min(image_scale_x, image_scale_y)
		if image_scalar > 1:
			# Never enlarge
			image_scalar = 1

		printed_size_mm = image_extents_mm * image_scalar
		page_dimensions_mm = self._hl_page.extents_mm
		offset_mm = (page_dimensions_mm - printed_size_mm) / 2
		offset_dots = offset_mm * 72 / 25.4
		printed_size_dots = printed_size_mm * 72 / 25.4
		params = {
			"xoffset":	offset_dots.width,
			"yoffset":	offset_dots.height,
			"xscalar":	printed_size_dots.width,
			"yscalar":	printed_size_dots.height,
		}

		self._hl_page.append_stream(textwrap.dedent("""\
		%(xscalar)f 0 0 %(yscalar)f %(xoffset)f %(yoffset)f cm
		/Img Do
		""" % (params)))

		page_obj = self._hl_page.page_obj
		if not PDFName("/Resources") in page_obj.content:
			page_obj.content[PDFName("/Resources")] = { }

		if not PDFName("/XObject") in page_obj.content[PDFName("/Resources")]:
			page_obj.content[PDFName("/Resources")][PDFName("/XObject")] = { }

		page_obj.content[PDFName("/Resources")][PDFName("/XObject")][PDFName("/Img")] = image.xref

class PDFImageFormatter(object):
	def __init__(self, best_chosen_pixel_format = PixelFormat.RGB, allow_lossy_compression = False, maximum_resolution_dpi = 600):
		self._allow_lossy_compression = allow_lossy_compression
		self._best_chosen_pixel_format = best_chosen_pixel_format
		self._maximum_resolution_dpi = maximum_resolution_dpi

	@classmethod
	def highlevel_color(cls):
		return cls(best_chosen_pixel_format = PixelFormat.RGB, allow_lossy_compression = True, maximum_resolution_dpi = 300)

	@classmethod
	def midlevel_color(cls):
		return cls(best_chosen_pixel_format = PixelFormat.RGB, allow_lossy_compression = True, maximum_resolution_dpi = 150)

	@classmethod
	def midlevel_gray(cls):
		return cls(best_chosen_pixel_format = PixelFormat.Grayscale, allow_lossy_compression = True, maximum_resolution_dpi = 150)

	@classmethod
	def lowlevel_bw(cls):
		return cls(best_chosen_pixel_format = PixelFormat.BlackWhite, allow_lossy_compression = True, maximum_resolution_dpi = 100)

	def reformat(self, pdfimage):
		conversion = { }

		if pdfimage.pixel_format > self._best_chosen_pixel_format:
			conversion["pixel_format"] = self._best_chosen_pixel_format
			new_pixel_format = self._best_chosen_pixel_format
		else:
			new_pixel_format = pdfimage.pixel_format

		if self._allow_lossy_compression and (new_pixel_format >= PixelFormat.Grayscale):
			conversion["image_format"] = "jpeg"
		else:
			if new_pixel_format in [ PixelFormat.BlackWhite, PixelFormat.Grayscale ]:
				conversion["image_format"] = "gray"
			else:
				conversion["image_format"] = "rgb"

		current_resolution = max(pdfimage.resolution_dpi)
		if current_resolution > self._maximum_resolution_dpi:
			conversion["resolution_dpi"] = self._maximum_resolution_dpi

		return pdfimage.convert_to(**conversion)
