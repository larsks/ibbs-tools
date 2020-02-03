import click
import syncterm
import sys

magiterm_connection_types = ['ssh', 'telnet']

magiterm_template = '''
[{name}]
address = {address}
port = {port}
conn type = {magiterm_conn_type}
'''


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
            for bbs in bbslist:
                bbs['magiterm_conn_type'] = magiterm_connection_types.index(
                        bbs['connectiontype'].lower())
                outputfile.write(magiterm_template.format(**bbs))


if __name__ == '__main__':
    main()
