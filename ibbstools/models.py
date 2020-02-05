import datetime
import peewee

BBSDB = peewee.SqliteDatabase(None,
                              pragmas=(('foreign_keys', 'on'),))


class Import(peewee.Model):
    name = peewee.TextField(unique=True)
    address = peewee.TextField()
    port = peewee.IntegerField()
    method = peewee.TextField()

    class Meta:
        database = BBSDB


class BBS(peewee.Model):
    name = peewee.TextField(unique=True)
    address = peewee.TextField()
    port = peewee.IntegerField()
    method = peewee.TextField()
    created_date = peewee.DateTimeField(
        constraints=[peewee.SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        database = BBSDB


class Status(peewee.Model):

    bbs = peewee.ForeignKeyField(
        BBS,
        backref='checks',
        on_delete='CASCADE')
    check_date = peewee.DateTimeField()
    status = peewee.TextField()

    class Meta:
        database = BBSDB
