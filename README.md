CPUCompare [![Build Status](https://travis-ci.org/muflone/cpucompare.svg?branch=master)](https://travis-ci.org/muflone/cpucompare)
==========
**Description:** A GTK+ application to make comparisons between CPU models.

**Copyright:** 2013-2022 Fabio Castelli (Muflone) <muflone@muflone.com>

**License:** GPL-3+

**Source code:** https://github.com/muflone/cpucompare

**Documentation:** http://www.muflone.com/cpucompare/

System Requirements
-------------------

* Python >= 3.6 (developed and tested for Python 3.9 and 3.10)
* XDG library for Python 3 ( https://pypi.org/project/pyxdg/ )
* GTK+ 3.0 libraries for Python 3
* GObject libraries for Python 3 ( https://pypi.org/project/PyGObject/ )

Installation
------------

A distutils installation script is available to install from the sources.

To install in your system please use:

    cd /path/to/folder
    python3 setup.py install

To install the files in another path instead of the standard /usr prefix use:

    cd /path/to/folder
    python3 setup.py install --root NEW_PATH

Usage
-----

If the application is not installed please use:

    cd /path/to/folder
    python3 cpucompare.py

If the application was installed simply use the cpucompare command.
