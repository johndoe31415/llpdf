import setuptools

with open("README.md") as f:
	long_description = f.read()

setuptools.setup(
	name = "llpdf",
	packages = setuptools.find_packages(),
	version = "0.0.4",
	license = "gpl-3.0",
	description = "Low-level PDF library",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	author = "Johannes Bauer",
	author_email = "joe@johannes-bauer.com",
	url = "https://github.com/johndoe31415/llpdf",
	download_url = "https://github.com/johndoe31415/llpdf/archive/0.0.4.tar.gz",
	keywords = [ "pdf", "reader", "writer", "document", "parser" ],
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3 :: Only",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",
	],
)
