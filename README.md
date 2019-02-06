# llpdf
llpdf is a PDF manipulation library that I originally wrote for pdfminify, but
that has other purposes as well for which I've now made it its own separate
project. Note that the API is changed to that of pdfminify so that pdfminify
isn't actually compatible anymore with the latest llpdf version. It's something
I anticipate fixing soonish.

llpdf uses its own PDF parser because for the particular purpose of low
manipulation of PDFs, neither PyPDF2 nor pdfrw (which I both tried to use)
seemed particularly suitable. It exposes all the internal structure of a PDF
file to the user and doesn't try to provide any "nice" abstraction. This makes
it very powerful, but also not particularly suitable for end-users. Usages for
llpdf that I've worked with are minifying PDFs (pdfminify!), signing PDFs,
manipulating PDFs (including images and text).

## Acknowledgments
llpdf uses the Toy Parser Generator (TPG) of Christophe Delord
(http://cdsoft.fr/tpg/). It is included (tpg.py file) and licensed under the
GNU LGPL v2.1 or any later version. Despite its name, it is far from a toy. In
fact, it is the most beautiful parser generator I have ever worked with and
makes grammars and parsing exceptionally easy, even for people without any
previous parsing experience. If you need parsing and use Python, TPG is *the*
go-to solution I would recommend. Seriously, it's amazing. Check it out.
Copyright and license details can be found in EXTERNAL_LICENSES.md.

In order to be able to easily create PDF/A-1b files, pdfminify also includes
the ICC sRGB color profile "sRGB_IEC61966-2-1_black scaled.icc". It is
distributed under its own license which is included in the EXTERNAL_LICENSES.md
file.

When signing documents, a Type1 font is included in the resulting PDF in order
to display metadata about the generated signature. As a default font, one of
the Bitstream Charter fonts which was contributed to the X consortium
(Bitstream Charter Serif) is included with pdfminify. It also has its own
copyright and license notice in EXTERNAL_LICENSES.md.

## License
pdfminify is licensed under the GNU GPL v3 (except for external components as
TPG, which has its own license). Later versions of the GPL are explicitly
excluded.

TPG (Toy Parser Generator), the ICC sRGB color profile and the Bitstream
Charter font fall under their respective licenses (see EXTERNAL_LICENSES.md).

