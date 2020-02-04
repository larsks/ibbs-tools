import peewee

BBSDB = peewee.SqliteDatabase(None)


class BBS(peewee.Model):
    name = peewee.TextField(unique=True)
    address = peewee.TextField()
    port = peewee.IntegerField()
    method = peewee.TextField()

    class Meta: # NOQA
        database = BBSDB


class Status(peewee.Model):

    bbs = peewee.ForeignKeyField(BBS, backref='checks')
    checked = peewee.DateTimeField()
    status = peewee.TextField()

    class Meta: # NOQA
        database = BBSDB
