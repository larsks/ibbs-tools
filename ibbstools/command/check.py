import asyncio
import click
import datetime
import enum
import errno
import fnmatch
import logging
import socket

import concurrent.futures

import ibbstools.syncterm
from ibbstools.models import BBSDB, BBS, Status

LOG = logging.getLogger(__name__)


class STATUS(enum.Enum):
    OPEN = 0
    TIMEOUT = 1
    REFUSED = 2
    UNKNOWN = 3
    UNREACHABLE = 4
    OTHER = 10


def try_connect(host, port, timeout=10):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, int(port)))
        s.shutdown(socket.SHUT_RDWR)
    except socket.timeout:
        LOG.debug('connection failed: timeout')
        return STATUS.TIMEOUT
    except ConnectionRefusedError:
        LOG.debug('connection failed: refused')
        return STATUS.REFUSED
    except socket.gaierror:
        LOG.debug('connection failed: hostname unknown')
        return STATUS.UNKNOWN
    except OSError as err:
        LOG.error('connection failed: %s: %s', type(err), err)
        if err.errno == errno.EHOSTUNREACH:
            return STATUS.UNREACHABLE
        else:
            return STATUS.OTHER
    except Exception as err:
        LOG.error('connection failed: %s: %s', type(err), err)
        return STATUS.OTHER
    else:
        return STATUS.OPEN


@click.option('-i', '--input', 'inputfile',
              default='syncterm.lst')
@click.option('-d', '--database', default='bbsdb.sqlite')
@click.option('-t', '--timeout', type=int, default=10)
@click.argument('patterns', nargs=-1)
def check(inputfile, database, timeout, patterns):
    BBSDB.init(database)
    BBSDB.connect()
    BBSDB.create_tables([BBS, Status])

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

            status = try_connect(bbs['address'],
                                 bbs['port'],
                                 timeout=timeout)

            statusref = Status(bbs=bbsref,
                               checked=now,
                               status=str(status).split('.')[1])

            bbsref.save()
            statusref.save()


async def async_try_connect(bbs, sem, timeout=None):
    name = bbs['name']
    host = bbs['address']
    port = int(bbs['port'])

    async with sem:
        LOG.info('%s: checking %s:%d', name, host, port)
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=timeout)
            writer.close()
            await writer.wait_closed()
        except (socket.timeout, concurrent.futures.TimeoutError):
            LOG.debug('%s: connection failed: timeout', name)
            status = STATUS.TIMEOUT
        except ConnectionRefusedError:
            LOG.debug('%s: connection failed: refused', name)
            status = STATUS.REFUSED
        except socket.gaierror:
            LOG.debug('%s: connection failed: hostname unknown', name)
            status = STATUS.UNKNOWN
        except OSError as err:
            LOG.error('%s: connection failed: %s: %s', name, type(err), err)
            if err.errno == errno.EHOSTUNREACH:
                status = STATUS.UNREACHABLE
            else:
                status = STATUS.OTHER
        except Exception as err:
            LOG.error('%s: connection failed: %s: %s', name, type(err), err)
            status = STATUS.OTHER
        else:
            status = STATUS.OPEN

    LOG.info('%s: %s', name, status)
    return (bbs, status)


@click.option('-i', '--input', 'inputfile',
              default='syncterm.lst')
@click.option('-d', '--database', default='bbsdb.sqlite')
@click.option('-t', '--timeout', type=int, default=10)
@click.option('-m', '--max-concurrency', type=int, default=10)
@click.argument('patterns', nargs=-1)
@click.pass_context
def check_async(ctx, inputfile, database, timeout, max_concurrency, patterns):
    # suppress peewee debug logging unless verbose >= 3 (-vvv)
    if ctx.obj.verbose < 3:
        peewee_logger = logging.getLogger('peewee')
        peewee_logger.setLevel('WARNING')

    BBSDB.init(database)
    BBSDB.connect()
    BBSDB.create_tables([BBS, Status])

    sync = ibbstools.syncterm.SynctermLst()
    now = datetime.datetime.utcnow()
    with open(inputfile, 'r') as fd:
        bbslist = sync.parse(fd)
        loop = asyncio.get_event_loop()

        if patterns:
            bbslist = (bbs for bbs in bbslist
                       if any(fnmatch.fnmatch(bbs['name'], pattern)
                              for pattern in patterns))

        sem = asyncio.Semaphore(max_concurrency)
        tasks = [async_try_connect(bbs, sem, timeout=timeout)
                 for bbs in bbslist]
        done, pending = loop.run_until_complete(
            asyncio.wait(tasks)
        )

    for result in done:
        bbs, status = result.result()
        bbsref, created = BBS.get_or_create(name=bbs['name'],
                                            address=bbs['address'],
                                            port=bbs['port'],
                                            method=bbs['connectiontype'])

        statusref = Status(bbs=bbsref,
                           checked=now,
                           status=str(status).split('.')[1])

        bbsref.save()
        statusref.save()
