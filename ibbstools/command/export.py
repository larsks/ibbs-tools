import click
import jinja2
import peewee
import sys

from ibbstools.models import BBSDB, BBS, Status
import ibbstools.filters


env = jinja2.Environment(
    loader=jinja2.PackageLoader('ibbstools', 'templates'))
env.filters = ibbstools.filters.filters


@click.option('-d', '--database', default='bbsdb.sqlite')
@click.option('-o', '--output', 'outputfile',
              type=click.File('w'),
              default=sys.stdout)
@click.option('-s', '--state',
              type=click.Choice(['up', 'down']))
@click.option('-f', '--format',
              type=click.Choice(
                  ['syncterm', 'magiterm', 'qodem', 'etherterm']),
              default='syncterm')
def export(database, state, format, outputfile):
    BBSDB.init(database)
    BBSDB.connect()

    bbslist = (
        BBS.select(BBS, Status)
        .join(Status)
        .order_by(BBS.name)
        .group_by(BBS.name)
        .having(Status.check_date == peewee.fn.MAX(Status.check_date))
    )

    if state == 'up':
        bbslist = bbslist.having(Status.status == 'OPEN')
    elif state == 'down':
        bbslist = bbslist.having(Status.status != 'OPEN')

    template = env.get_template(f'format/{format}')

    with outputfile:
        outputfile.write(template.render(bbslist=bbslist))
