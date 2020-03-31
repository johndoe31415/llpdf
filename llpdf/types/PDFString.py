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

from .Comparable import Comparable

class PDFString(Comparable):
	def __init__(self, text):
		assert(isinstance(text, str))
		self._text = text
		try:
			self._encoding = self._text.encode("ascii")
		except UnicodeEncodeError:
			self._encoding = bytes.fromhex("fe ff") + self._text.encode("utf-16-BE")

	@property
	def text(self):
		return self._text

	def cmpkey(self):
		return ("PDFString", self.text)

	def __bytes__(self):
		return self._encoding

	def __repr__(self):
		return str(self)

	def __str__(self):
		return "String<%s>" % (self.text)
