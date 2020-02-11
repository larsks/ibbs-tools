import asyncio
import click
import datetime
import enum
import errno
import logging
import socket

import concurrent.futures

from ibbstools.models import BBSDB, BBS, Status

LOG = logging.getLogger(__name__)


class STATUS(enum.Enum):
    OPEN = 0
    TIMEOUT = 1
    REFUSED = 2
    UNKNOWN = 3
    UNREACHABLE = 4
    OTHER = 10


async def async_try_connect(bbs, sem, timeout=None):
    name = bbs.name
    host = bbs.address
    port = bbs.port

    # some listsings have the host address as user@host
    if '@' in host:
        user, host = host.split('@', 1)

    async with sem:
        LOG.info('%s: checking %s:%d', name, host, port)
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port, family=socket.AF_INET),
                timeout=timeout)
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
            LOG.debug('%s: connection failed: %s: %s', name, type(err), err)
            if err.errno == errno.EHOSTUNREACH:
                status = STATUS.UNREACHABLE
            else:
                LOG.error('%s: connection failed: %s: %s', name, type(err), err)
                status = STATUS.OTHER
        except Exception as err:
            LOG.error('%s: connection failed: %s: %s', name, type(err), err)
            status = STATUS.OTHER
        else:
            status = STATUS.OPEN

    LOG.info('%s: %s', name, status)
    return (bbs, status)


@click.option('-d', '--database', default='bbsdb.sqlite')
@click.option('-t', '--timeout', type=int, default=10)
@click.option('-m', '--max-concurrency', type=int, default=10)
@click.option('-n', '--no-update', is_flag=True)
def check_async(database, timeout, max_concurrency, no_update):
    BBSDB.init(database)
    BBSDB.connect()
    BBSDB.create_tables([BBS, Status])

    now = datetime.datetime.utcnow()
    loop = asyncio.get_event_loop()
    sem = asyncio.Semaphore(max_concurrency)
    bbslist = BBS.select()

    tasks = [async_try_connect(bbs, sem, timeout=timeout) for bbs in bbslist]
    done, pending = loop.run_until_complete(
        asyncio.wait(tasks)
    )

    if no_update:
        return

    summary = {}
    for result in done:
        bbs, status = result.result()

        status = str(status).split('.')[1]
        summary[status] = summary.get(status, 0) + 1

        statusref = Status(bbs=bbs,
                           check_date=now,
                           status=status)

        statusref.save()

    summary_parts = ['{} {}'.format(k, v)
                     for k, v in sorted(summary.items())]
    LOG.info(', '.join(summary_parts))
