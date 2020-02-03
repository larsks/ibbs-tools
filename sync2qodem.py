import click
import syncterm
import sys

qodem_template = '''
name={name}
address={address}
port={port}
username=
password=
tagged=false
doorway=config
method={qodem_method}
emulation=ANSI
codepage=CP437
quicklearn=false
use_modem_cfg=true
baud=115200
data_bits=8
parity=none
stop_bits=1
xonxoff=false
rtscts=true
lock_dte_baud=true
times_on=2
use_default_toggles=true
toggles=0
last_call=1580679969
script_filename=
capture_filename=
translate_8bit_filename=
translate_unicode_filename=
keybindings_filename=
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
                bbs['qodem_method'] = bbs['connectiontype'].upper()
                outputfile.write(qodem_template.format(**bbs))


if __name__ == '__main__':
    main()
