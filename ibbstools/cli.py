import click
import logging
import types

import ibbstools.command.check as check
import ibbstools.command.export as export
import ibbstools.command.import_list as import_list
import ibbstools.command.initdb as initdb
import ibbstools.command.render as render
import ibbstools.command.sync2json as sync2json
import ibbstools.command.sync2magi as sync2magi
import ibbstools.command.sync2qodem as sync2qodem


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

    # suppress peewee debug logging unless verbose >= 3 (-vvv)
    if verbose < 3:
        peewee_logger = logging.getLogger('peewee')
        peewee_logger.setLevel('WARNING')


main.command(name='sync2magi')(sync2magi.sync2magi)
main.command(name='sync2qodem')(sync2qodem.sync2qodem)
main.command(name='sync2json')(sync2json.sync2json)
main.command(name='check')(check.check_async)
main.command(name='render')(render.render)
main.command(name='export')(export.export)
main.command(name='import')(import_list.import_list)
main.command(name='initdb')(initdb.initdb)


if __name__ == '__main__':
    main()
