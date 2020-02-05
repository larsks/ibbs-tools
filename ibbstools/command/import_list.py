import click
import logging
import peewee
import sys

import ibbstools.syncterm
from ibbstools.models import BBSDB, Import, BBS

LOG = logging.getLogger(__name__)


# Why isn't this named "import"? Because Python gets cranky if
# you try to name something "import".
@click.option('-d', '--database', default='bbsdb.sqlite')
@click.option('-i', '--input', 'inputfile',
              type=click.File('r'),
              default=sys.stdin)
def import_list(database, inputfile):
    BBSDB.init(database)
    BBSDB.connect()
    BBSDB.create_tables([Import, BBS])

    Import.delete().execute()

    sync = ibbstools.syncterm.SynctermLst()
    with inputfile:
        bbslist = sync.parse(inputfile)
        for bbs in bbslist:
            if bbs['name'].startswith('War'):
                continue
            LOG.debug('reading %s', bbs['name'])
            bbsref = Import.create(
                name=bbs['name'],
                address=bbs['address'].lower(),
                port=bbs['port'],
                method=bbs['connectiontype'].lower())

            bbsref.save()

        deleted = (
            BBS.select(BBS.id)
            .join(Import, peewee.JOIN.LEFT_OUTER,
                  on=(BBS.name == Import.name))
            .where(Import.name == None)  # NOQA
        )

        new = (
            Import.select(
                Import.name, Import.address, Import.port, Import.method
            )
            .join(BBS, peewee.JOIN.LEFT_OUTER,
                  on=(BBS.name == Import.name))
            .where(BBS.name == None)  # NOQA
        )

        LOG.info('removing %d entries, adding %d entries',
                 len(deleted),
                 len(new))

        BBS.delete().where(BBS.id.in_(deleted)).execute()
        BBS.insert_from(
            new,
            fields=[BBS.name, BBS.address, BBS.port, BBS.method]).execute()
