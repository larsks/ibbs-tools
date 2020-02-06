import datetime
import peewee

BBSDB = peewee.SqliteDatabase(None,
                              pragmas=(('foreign_keys', 'on'),))


class Base(peewee.Model):
    class Meta:
        database = BBSDB


class Import(Base):
    name = peewee.TextField(unique=True)
    address = peewee.TextField()
    port = peewee.IntegerField()
    method = peewee.TextField()


class BBS(Base):
    name = peewee.TextField(unique=True)
    address = peewee.TextField()
    port = peewee.IntegerField()
    method = peewee.TextField()
    created_date = peewee.DateTimeField(
        constraints=[peewee.SQL('DEFAULT CURRENT_TIMESTAMP')])


class Status(Base):

    bbs = peewee.ForeignKeyField(
        BBS,
        backref='checks',
        on_delete='CASCADE')
    check_date = peewee.DateTimeField()
    status = peewee.TextField()
