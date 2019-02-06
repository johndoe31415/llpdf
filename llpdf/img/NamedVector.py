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

class NamedVector(object):
	_COMPONENTS = None

	def __init__(self, *values, **kwargs):
		if (len(values) == len(self._COMPONENTS)) and (len(kwargs) == 0):
			self._values = tuple(values)
		elif (len(kwargs) == len(self._COMPONENTS)) and (len(values) == 0):
			self._values = tuple(kwargs[key] for key in self._COMPONENTS)
		else:
			if (len(values) > 0) and (len(kwargs) > 0):
				raise Exception("Can only specify args or kwargs, not mix the two")
			else:
				raise Exception("Agument count mismatch (expected %d)." % (len(self._COMPONENTS)))

	def __getattr__(self, key):
		return self._values[self._COMPONENTS.index(key)]

	def __iter__(self):
		return iter(self._values)

	def __add__(self, other):
		return self.__class__(*((x + y) for (x, y) in zip(self, other)))

	def __mul__(self, scalar):
		return self.__class__(*((x * scalar) for x in self))

	def __truediv__(self, dividend):
		return self * (1 / dividend)

	def __sub__(self, other):
		return self + (-other)

	def __neg__(self):
		return self.__class__(*(-x for x in self))

	def __len__(self):
		return len(self._values)

	def __str__(self):
		return "%s<%s>" % (self.__class__.__name__, ", ".join("%.3f" % (x) for x in self))
