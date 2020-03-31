#	llpdf - Low-level PDF library in native Python.
#	Copyright (C) 2016-2016 Johannes Bauer
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

from .PDFFilter import PDFFilter
from llpdf.types.PDFName import PDFName
from llpdf.Measurements import Measurements

class AddCropBoxFilter(PDFFilter):
	def run(self):
		native_values = [ Measurements.convert(value, self._args.unit, "native") for value in self._args.cropbox ]
		native_cropbox = [ native_values[0], native_values[1], native_values[0] + native_values[2], native_values[1] + native_values[3] ]
		for page in self._pdf.pages:
			page.content[PDFName("/CropBox")] = native_cropbox
