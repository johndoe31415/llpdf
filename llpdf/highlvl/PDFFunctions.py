#	llpdf - Tool to minify PDF files.
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

from llpdf import PDFName, PDFString
from llpdf.types.Timestamp import Timestamp
from llpdf.EncodeDecode import EncodedObject
from llpdf.img.PDFExtImage import Dimensions

class HighlevelPDFPage():
	def __init__(self, pdf, page_object, contents_object):
		self._pdf = pdf
		self._page_obj = page_object
		self._contents_obj = contents_object

	@property
	def extents_mm(self):
		mediabox = self.page_obj.content[PDFName("/MediaBox")]
		return Dimensions(width = mediabox[2] / 72 * 25.4, height = mediabox[3] / 72 * 25.4)

	@property
	def pdf(self):
		return self._pdf

	@property
	def page_obj(self):
		return self._page_obj

	@property
	def contents_obj(self):
		return self._contents_obj

	def append_stream(self, text):
		new_data = text.encode("utf-8")
		if self.contents_obj.stream is not None:
			prev_data = self.contents_obj.stream.decode()
			new_data = prev_data + b"\n" + new_data
		self.contents_obj.set_stream(EncodedObject.create(new_data))

	def __str__(self):
		return "Page<%s>" % (self.page_obj.xref)

class HighlevelPDFFunctions():
	def __init__(self, pdf):
		self._pdf = pdf

	def initialize_pages(self, title = None, author = None):
		pages_object = self._pdf.new_object({
			PDFName("/Type"):	PDFName("/Pages"),
			PDFName("/Count"):	0,
			PDFName("/Kids"):	[ ],
		}).xref

		root_object = self._pdf.new_object({
			PDFName("/Type"):	PDFName("/Catalog"),
			PDFName("/Pages"):	pages_object,
		}).xref

		info_object = self._pdf.new_object({
			PDFName("/Producer"):		b"llpdf",
			PDFName("/CreationDate"):	Timestamp.localnow().format_pdf().encode("ascii"),
		})
		if title is not None:
			info_object.content[PDFName("/Title")] = PDFString(title)
		if author is not None:
			info_object.content[PDFName("/Author")] = PDFString(author)

		self._pdf.trailer[PDFName("/Root")] = root_object
		self._pdf.trailer[PDFName("/Info")] = info_object.xref


	def new_page(self, width_mm = 210, height_mm = 297):
		pages_object = self._pdf.pages_object

		contents_object = self._pdf.new_object()

		page_object = self._pdf.new_object({
			PDFName("/Type"):		PDFName("/Page"),
			PDFName("/Parent"):		pages_object.xref,
			PDFName("/Contents"):	contents_object.xref,
			PDFName("/MediaBox"):	[ 0, 0, width_mm / 25.4 * 72, height_mm / 25.4 * 72 ],
		})

		pages_object.content[PDFName("/Count")] = pages_object.content[PDFName("/Count")] + 1
		pages_object.content[PDFName("/Kids")].append(page_object.xref)

		return HighlevelPDFPage(pdf = self._pdf, page_object = page_object, contents_object = contents_object)
