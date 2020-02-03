This is a collection of utilities for processing the [Telnet BBS List][].

[telnet bbs list ]: https://www.telnetbbsguide.com/

## Files in this repository

- `syncterm.py`

  Defines the `SynctermLst` class for reading `syncterm.lst` format files.

- `sync2json.py`

  Dump `syncterm.lst` as a JSON document.

- `sync2magi.py`

  Produce a MagiTerm format dialing directory from `syncterm.lst`

- `sync2qodem.py`

  Produce a qodem format dialing directory from `syncterm.lst`
