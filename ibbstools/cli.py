import click

import ibbstools.command.sync2magi as sync2magi
import ibbstools.command.sync2qodem as sync2qodem
import ibbstools.command.sync2json as sync2json


@click.group()
def main():
    pass


main.command(name='sync2magi')(sync2magi.command)
main.command(name='sync2qodem')(sync2qodem.command)
main.command(name='sync2json')(sync2json.command)


@main.command()
def check():
    pass


if __name__ == '__main__':
    main()
