import click
import re


class SynctermLst(object):
    re_title = re.compile(r'\[(?P<name>.*)\]')
    re_option = re.compile(r'\s*(?P<name>\S+) *=(?P<value>.*)')

    def parse(self, fd):
        cur = None

        for line in fd:
            mo = self.re_title.match(line)
            if mo:
                if cur is not None:
                    yield(cur)

                name = mo.group('name')
                cur = {'name': name}
                continue
            mo = self.re_option.match(line)
            if mo and cur is not None:
                name = mo.group('name').lower().strip()
                value = mo.group('value')
                cur[name] = value

        yield(cur)
