import datetime
import peewee

BBSDB = peewee.SqliteDatabase(None)


class BBS(peewee.Model):
    name = peewee.TextField(unique=True)
    address = peewee.TextField()
    port = peewee.IntegerField()
    method = peewee.TextField()
    created_date = peewee.DateTimeField(default=datetime.datetime.utcnow)

    class Meta:
        database = BBSDB


class Status(peewee.Model):

    bbs = peewee.ForeignKeyField(BBS, backref='checks')
    check_date = peewee.DateTimeField()
    status = peewee.TextField()

    class Meta:
        database = BBSDB
