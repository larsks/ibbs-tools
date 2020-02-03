import click
import socket
import sqlite3
import syncterm


@click.command()
@click.option('-i', '--input', 'inputfile', default='syncterm.lst')
@click.option('-d', '--database', default='bbsdb.sqlite')
def main(inputfile, database):
    sync = syncterm.SynctermLst()
    with open(inputfile, 'r') as fd:
        bbslist = sync.parse(fd)
        bbsdb = sqlite3.connect(database)

        for bbs in bbslist:
            ...


if __name__ == '__main__':
    main()
