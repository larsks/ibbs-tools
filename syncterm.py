import click
import re


class SynctermLst(object):
    re_title = re.compile(r'\[(?P<name>.*)\]')
    re_option = re.compile(r'\s*(?P<name>\S+) *=(?P<value>.*)')

    def parse(self, fd):
        cur = default = {}

        for line in fd:
            mo = self.re_title.match(line)
            if mo:
                if cur is not default:
                    yield(cur)

                name = mo.group('name')
                cur = dict(default)
                cur['name'] = name
                continue
            mo = self.re_option.match(line)
            if mo:
                name = mo.group('name').lower()
                value = mo.group('value')
                cur[name] = value

        yield(cur)
