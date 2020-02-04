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
def render(database, outputfile):
    BBSDB.init(database)

    bbslist = (
        Status.select(Status, BBS)
        .join(BBS)
        .order_by(BBS.name)
        .group_by(Status.bbs)
        .having(Status.checked == peewee.fn.MAX(Status.checked))
    )

    template = env.get_template('bbslist.html')

    with outputfile:
        outputfile.write(template.render(
            bbslist=bbslist,
            get_bbs_status=get_bbs_status,
            status_to_char=status_to_char))
