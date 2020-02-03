import click
import json
import syncterm
import sys


@click.command()
@click.option('-i', '--input', 'inputfile',
              default='syncterm.lst')
@click.option('-o', '--output', 'outputfile',
              type=click.File('w'), default=sys.stdout)
def main(inputfile, outputfile):
    sync = syncterm.SynctermLst()
    with open(inputfile, 'r') as fd:
        bbslist = sync.parse(fd)

        with outputfile:
            json.dump(list(bbslist), outputfile, indent=2)


if __name__ == '__main__':
    main()
