from peewee import *
import string
import random
import datetime

db = SqliteDatabase("database.db")


class BaseModel(Model):
    class Meta:
        database = db


class Family(BaseModel):
    id = PrimaryKeyField(null=False)
    name = CharField(null=False)
    date_created = DateTimeField(null=False)

    def get_members(self):
        members_list = Member.select().where(Member.family == self.id)
        return members_list


class Member(BaseModel):
    id = PrimaryKeyField(null=False)
    family = ForeignKeyField(Family)
    name = CharField(null=False)
    admin_status = BooleanField(default=0)
    date_joined = DateTimeField(null=False)


class Operation(BaseModel): # ON CONSTRUCT, NOT ADDED TO DATABASE
    id = AutoField()
    family = ForeignKeyField(Family)
    member = ForeignKeyField(Member)
    total = FloatField(default=0.00, null=False)
    desc = CharField(default="Описание операции")
    date_registered = DateTimeField(null=False)


class Task(BaseModel):  # ON CONSTRUCT, NOT ADDED TO DATABASE
    id = AutoField()
    from_member = ForeignKeyField(Member)
    to_member = ForeignKeyField(Member)


db.connect()
db.create_tables([Family, Member])


# ------------------------------------------------------------- OP'S FOR MEMBER MODULE ---------------------------------
def get_member_by_id(tg_id):
    member = Member.get_or_none(Member.id == tg_id)
    if not member:
        return False
    else:
        return member


def create_member(tg_id, family_id, name, admin_status=0):
    date_joined = datetime.datetime.today().strftime("%d.%m.%Y")
    member = Member.create(
        id=tg_id, family=family_id, name=name, admin_status=admin_status, date_joined=date_joined
    )
    member.save()
    return member


# --------------------------------------------------------- OP'S FOR FAMILY MODULE -------------------------------------
def get_family_by_id(family_id):
    family = Family.get_or_none(Family.id == family_id)
    if family:
        return family
    else:
        return False


def create_family(name: str):
    family_id = generate_random_id()
    date_created = datetime.datetime.today()
    date_created = date_created.strftime("%d.%m.%Y")
    new_family = Family.create(id=family_id, name=name, date_created=date_created)
    new_family.save()
    return new_family


def get_families_id():
    family_list = list()
    families = Family.select()
    for x in families:
        family_list.append(str(x.id))
    return family_list


# ------------------------------------------------------------ BASIC-OPS ----------------------------------------------
def generate_random_id():
    result = ""
    for x in range(6):
        symbol = random.choice(string.digits)
        result = result + symbol

    family_check = Family.get_or_none(Family.id == result)
    if not family_check:
        return int(result)
    else:
        generate_random_id()
