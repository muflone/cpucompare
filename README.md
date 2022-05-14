CPUCompare [![Build Status](https://travis-ci.org/muflone/cpucompare.svg?branch=master)](https://travis-ci.org/muflone/cpucompare)
==========
**Description:** A GTK+ application to make comparisons between CPU models.

**Copyright:** 2013-2022 Fabio Castelli (Muflone) <muflone@muflone.com>

**License:** GPL-3+

**Source code:** https://github.com/muflone/cpucompare

**Documentation:** http://www.muflone.com/cpucompare/

System Requirements
-------------------

* Python 2.x (developed and tested for Python 2.7.5)
* GTK+ 3.0 libraries for Python 2.x
* GObject libraries for Python 2.x
* XDG library for Python 2.x
* SQLite3 library for Python 2.x (usually shipped with Python distribution)
* Distutils library for Python 2.x (usually shipped with Python distribution)

Installation
------------

A distutils installation script is available to install from the sources.

To install in your system please use:

    cd /path/to/folder
    python2 setup.py install

To install the files in another path instead of the standard /usr prefix use:

    cd /path/to/folder
    python2 setup.py install --root NEW_PATH

Usage
-----

If the application is not installed please use:

    cd /path/to/folder
    python2 cpucompare.py

If the application was installed simply use the cpucompare command.
