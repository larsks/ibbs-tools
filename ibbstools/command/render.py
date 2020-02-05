import click
import itertools
import jinja2
import peewee
import sys

from pathlib import Path

import ibbstools.filters
from ibbstools.models import BBSDB, BBS, Status

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
        .order_by(Status.check_date)
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
@click.argument('template', type=Path)
def render(database, state, property, outputfile, template):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template.parent)))
    env.filters = ibbstools.filters.filters
    t = env.get_template(str(template.name))

    BBSDB.init(database)
    BBSDB.connect()

    properties = dict(x.split('=') for x in property)

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

    status_summary = (
        Status.select(Status.check_date,
                      Status.status,
                      peewee.fn.Count(Status.id).alias('count'))
        .group_by(Status.check_date, Status.status)
        .order_by(Status.check_date, Status.status)
    )

    status_summary = itertools.groupby(status_summary, lambda x: x.check_date)
    status_summary = [
        {'date': date, 'summary': {x.status: x.count for x in results}}
        for date, results in status_summary
    ]

    with outputfile:
        outputfile.write(t.render(
            bbslist=bbslist,
            status_summary=status_summary,
            get_bbs_status=get_bbs_status,
            **properties))
