import click
import json
import sys

import ibbstools.syncterm


@click.option('-i', '--input', 'inputfile',
              default='syncterm.lst')
@click.option('-o', '--output', 'outputfile',
              type=click.File('w'), default=sys.stdout)
def sync2json(inputfile, outputfile):
    sync = ibbstools.syncterm.SynctermLst()
    with open(inputfile, 'r') as fd:
        bbslist = sync.parse(fd)

        with outputfile:
            json.dump(list(bbslist), outputfile, indent=2)
