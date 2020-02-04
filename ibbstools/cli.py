import click
import logging

import ibbstools.command.sync2magi as sync2magi
import ibbstools.command.sync2qodem as sync2qodem
import ibbstools.command.sync2json as sync2json
import ibbstools.command.check as check


@click.group()
@click.option('-v', '--verbose', count=True)
def main(verbose):
    try:
        loglevel = [logging.WARNING, logging.INFO, logging.DEBUG][verbose]
    except IndexError:
        loglevel = logging.DEBUG

    logging.basicConfig(level=loglevel)


main.command(name='sync2magi')(sync2magi.command)
main.command(name='sync2qodem')(sync2qodem.command)
main.command(name='sync2json')(sync2json.command)
main.command(name='check')(check.command)


if __name__ == '__main__':
    main()
