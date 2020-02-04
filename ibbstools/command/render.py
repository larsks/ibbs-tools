import click
import peewee
import sys

import jinja2

from ibbstools.models import BBSDB, BBS, Status

env = jinja2.Environment(
    loader=jinja2.PackageLoader('ibbstools', 'templates'))

status_to_char = {
    'OPEN': 'o',
    'UNREACHABLE': 'u',
    'UNKNOWN': 'h',
    'REFUSED': 'r',
    'TIMEOUT': 't',
    'OTHER': '?',
}


def get_bbs_status(bbs, n=10):
    status = (
        Status.select(Status, BBS)
        .join(BBS)
        .where(Status.bbs == bbs)
        .order_by(Status.checked)
        .limit(n)
    )

    return status


@click.option('-d', '--database', default='bbsdb.sqlite')
@click.option('-o', '--output', 'outputfile',
              type=click.File('w'),
              default=sys.stdout)
@click.option('-s', '--state',
              type=click.Choice(['up', 'down']))
@click.option('-p', '--property', multiple=True)
def render(database, state, property, outputfile):
    BBSDB.init(database)

    properties = dict(x.split('=') for x in property)

    bbslist = (
        BBS.select(BBS, Status)
        .join(Status)
        .order_by(BBS.name)
        .group_by(BBS.name)
        .having(Status.checked == peewee.fn.MAX(Status.checked))
    )

    if state == 'up':
        bbslist = bbslist.having(Status.status == 'OPEN')
    elif state == 'down':
        bbslist = bbslist.having(Status.status != 'OPEN')

    template = env.get_template('bbslist.html')

    with outputfile:
        outputfile.write(template.render(
            bbslist=bbslist,
            get_bbs_status=get_bbs_status,
            **properties))
