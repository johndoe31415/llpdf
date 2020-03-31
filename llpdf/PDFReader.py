#	llpdf - Low-level PDF library in native Python.
#	Copyright (C) 2016-2020 Johannes Bauer
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

import logging
from llpdf.PDFDocument import PDFDocument
from llpdf.repr import PDFParser
from .types.PDFObject import PDFObject
from llpdf.types.PDFName import PDFName
from .types.XRefTable import XRefTable
from .FileRepr import StreamRepr

class PDFReader(object):
	_log = logging.getLogger("llpdf.PDFReader")

	def _read_identifying_header(self, f):
		f.seek(0)
		version = f.readline()

		pos = f.tell()
		after_hdr = f.readline()
		if (after_hdr[0] != ord("%")) or any(value & 0x80 != 0x80 for value in after_hdr[ 1 : 5 ]):
			self._log.warning("PDF seems to violate standard, bytes read in second line are %s.", after_hdr)
			f.seek(pos)
		return version.rstrip(b"\r\n ")

	def _read_pdf_body(self, f, pdf):
		generation = 0
		while True:
			generation += 1
			self._log.debug("Trying to read generation %d data at offset 0x%x", generation, f.tell())
			objcnt = self._read_objects(f, pdf)
			if objcnt == 0:
				self._log.debug("No more data to read at 0x%x.", f.tell())
				break
			self._read_endfile(f, pdf)

	def _read_objects(self, f, pdf):
		self._log.debug("Started reading objects at 0x%x.", f.tell())
		objcnt = 0
		while True:
			obj = PDFObject.parse(f)
			if obj is None:
				break
			objcnt += 1
			self._log.debug("Read object: %s", obj)
			pdf.add(obj)
		self._log.debug("Finished reading %d objects at 0x%x.", objcnt, f.tell())
		return objcnt

	def _read_endfile(self, f, pdf):
		self._log.debug("Reading end-of-file data at 0x%x.", f.tell())
		while True:
			line = self._read_textline(f).strip("\r\n ")
			if line == "":
				continue
			elif line == "xref":
				xref_table = XRefTable.read_xref_table_from_file(f)
			elif line == "trailer":
				trailer = self._read_trailer(f)
				pdf.trailer = trailer
			elif line == "startxref":
				xref_offset = int(f.readline())
				if len(pdf.trailer) == 0:
					# Compressed XRef directory
					with f.tempseek(xref_offset) as marker:
						self._log.trace("Will parse XRef stream at offset 0x%x referenced from 0x%x." % (xref_offset, marker.prev_offset))
						xref_object = PDFObject.parse(f)
						if xref_object is None:
							self._log.error("Could not parse a valid type /XRef object at 0x%x. Corrupt PDF?", xref_offset)
						else:
							trailer = xref_object.content
							assert(trailer[PDFName("/Type")] == PDFName("/XRef"))
							pdf.trailer = trailer
							pdf.xref_table.parse_xref_object(xref_object.stream.decode(), pdf.trailer.get(PDFName("/Index")), pdf.trailer[PDFName("/W")])
			elif line == "%%EOF":
				self._log.debug("Hit EOF marker at 0x%x.", f.tell())
				break
			else:
				raise Exception("Unknown end file token '%s' at offset 0x%x." % (line, f.tell()))

	def _read_textline(self, f):
		line = f.readline_nonempty().decode("ascii").rstrip("\r\n")
		return line

	def _read_trailer(self, f):
		self._log.debug("Started reading trailer at 0x%x.", f.tell())
		trailer_data = f.read_until_token(b"startxref", rewind = True)
		trailer_data = trailer_data.decode("latin1")
		trailer = PDFParser.parse(trailer_data)
		return trailer

	def _get_pages_from_pages_obj(self, pages_obj):
		pagecontent_xrefs = pages_obj.content[PDFName("/Kids")]
		for page_xref in pagecontent_xrefs:
			page = self.lookup(page_xref)
			if page.content[PDFName("/Type")] == PDFName("/Page"):
				yield page
			elif page.content[PDFName("/Type")] == PDFName("/Pages"):
				yield from self._get_pages_from_pages_obj(page)
			else:
				raise Exception("Page object %s contains neither page nor pages (/Type = %s)." % (pages_obj, page.content[PDFName("/Type")]))

#	def read_stream(self):
#		self._f.read_until([ b"stream\r\n", b"stream\n" ])
#		(data, terminal) = self._f.read_until([ b"endstream\r\n", b"endstream\n" ])
#		return data

	def read(self, filename):
		pdf = PDFDocument()
		with open(filename, "rb") as f:
			pdf_data = f.read()
		f = StreamRepr(pdf_data)

		hdr_version = self._read_identifying_header(f)
		self._log.debug("Header detected: %s", str(hdr_version))
		if hdr_version not in [ b"%PDF-1.3", b"%PDF-1.4", b"%PDF-1.5", b"%PDF-1.6", b"%PDF-1.7" ]:
			self._log.warning("Warning: Header indicates %s, unknown if we can handle this.", hdr_version.decode())

		self._read_pdf_body(f, pdf)
		self._log.debug("Finished reading PDF file. %d objects found.", pdf.objcount)
		pdf.unpack_objstrms()
		self._log.debug("Finished unpacking all object streams in file. %d objects found total.", pdf.objcount)
		return pdf
