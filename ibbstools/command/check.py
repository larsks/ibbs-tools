import click
import datetime
import enum
import fnmatch
import logging
import peewee
import socket

import ibbstools.syncterm

LOG = logging.getLogger(__name__)
BBSDB = peewee.SqliteDatabase(None)


class STATUS(enum.Enum):
    OPEN = 0
    TIMEOUT = 1
    REFUSED = 2
    OTHER = 3


class BBS(peewee.Model):
    name = peewee.TextField(unique=True)
    address = peewee.TextField()
    port = peewee.IntegerField()
    method = peewee.TextField()

    class Meta:
        database = BBSDB


class Check(peewee.Model):

    bbs = peewee.ForeignKeyField(BBS, backref='checks')
    when = peewee.DateTimeField()
    status = peewee.TextField()

    class Meta:
        database = BBSDB


def try_connect(host, port, timeout=10):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, int(port)))
        s.shutdown(socket.SHUT_RDWR)
    except socket.timeout:
        return STATUS.TIMEOUT
    except ConnectionRefusedError:
        return STATUS.REFUSED
    except Exception as err:
        LOG.error('connection failed: %s', err)
        return STATUS.OTHER
    else:
        return STATUS.OPEN


@click.option('-i', '--input', 'inputfile',
              default='syncterm.lst')
@click.option('-d', '--database', default='bbsdb.sqlite')
@click.argument('patterns', nargs=-1)
def command(inputfile, database, patterns):
    BBSDB.init(database)
    BBSDB.connect()
    BBSDB.create_tables([BBS, Check])

    sync = ibbstools.syncterm.SynctermLst()
    now = datetime.datetime.utcnow()
    with open(inputfile, 'r') as fd:
        bbslist = sync.parse(fd)
        if patterns:
            bbslist = (bbs for bbs in bbslist
                       if any(fnmatch.fnmatch(bbs['name'], pattern)
                              for pattern in patterns))

        for bbs in bbslist:
            LOG.info('checking %s at %s:%s',
                     bbs['name'], bbs['address'], bbs['port'])
            bbsref, created = BBS.get_or_create(name=bbs['name'],
                                                address=bbs['address'],
                                                port=bbs['port'],
                                                method=bbs['connectiontype'])

            status = try_connect(bbs['address'], bbs['port'])

            check = Check(bbs=bbsref, when=now, status=status)

            bbsref.save()
            check.save()
