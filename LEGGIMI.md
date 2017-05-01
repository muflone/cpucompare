CPUCompare [![Build Status](https://travis-ci.org/muflone/cpucompare.svg?branch=master)](https://travis-ci.org/muflone/cpucompare)
==========
**Descrizione:** Un'applicazione GTK per effettuare confronti tra modelli di CPU.

**Copyright:** 2013-2017 Fabio Castelli (Muflone) <muflone(at)vbsimple.net>

**Licenza:** GPL-2+

**Codice sorgente:** https://github.com/muflone/cpucompare

**Documentazione:** http://www.muflone.com/cpucompare/

Requisiti di sistema
--------------------

* Python 2.x (sviluppato e testato per Python 2.7.5)
* Libreria GTK+3.0 per Python 2
* Libreria GObject per Python 2
* Libreria SQLite3 per Python 2 (generalmente fornita col pacchetto Python)
* Libreria Distutils per Python 2 (generalmente fornita col pacchetto Python)

Installazione
-------------

E' disponibile uno script di installazione distutils per installare da sorgenti.

Per installare nel tuo sistema utilizzare:

    cd /percorso/alla/cartella
    python2 setup.py install

Per installare i files in un altro percorso invece del prefisso /usr standard
usare:

    cd /percorso/alla/cartella
    python2 setup.py install --root NUOVO_PERCORSO

Utilizzo
--------

Se l'applicazione non è stata installata utilizzare:

    cd /path/to/folder
    python2 cpucompare.py

Se l'applicazione è stata installata utilizzare semplicemente il comando
cpucompare.
