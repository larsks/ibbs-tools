import click

from ibbstools.models import BBSDB, BBS, Status


@click.option('-d', '--database', default='bbsdb.sqlite')
def initdb(database):
    BBSDB.init(database)
    BBSDB.connect()
    BBSDB.create_tables([BBS, Status])
