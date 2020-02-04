import click
import logging
import types

import ibbstools.command.sync2magi as sync2magi
import ibbstools.command.sync2qodem as sync2qodem
import ibbstools.command.sync2json as sync2json
import ibbstools.command.check as check


config = types.SimpleNamespace()


@click.group()
@click.option('-v', '--verbose', count=True)
@click.pass_context
def main(ctx, verbose):
    ctx.obj = config
    config.verbose = verbose

    try:
        loglevel = [logging.WARNING, logging.INFO, logging.DEBUG][verbose]
    except IndexError:
        loglevel = logging.DEBUG

    logging.basicConfig(level=loglevel)


main.command(name='sync2magi')(sync2magi.sync2magi)
main.command(name='sync2qodem')(sync2qodem.sync2qodem)
main.command(name='sync2json')(sync2json.sync2json)
main.command(name='check')(check.check)
main.command(name='check_async')(check.check_async)


if __name__ == '__main__':
    main()
