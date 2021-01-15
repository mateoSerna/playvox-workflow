from .db import db
from mongoengine.queryset import queryset_manager


class User(db.Document):
    user_id = db.StringField(required=True, unique=True)
    pin = db.IntField(required=True)
    balance = db.DecimalField(required=True, default=0)


class Step(db.EmbeddedDocument):
    id = db.StringField(required=True)
    params = db.DictField(required=True)
    action = db.StringField(required=True)
    transitions = db.ListField(db.DictField())


class Trigger(db.EmbeddedDocument):
    id = db.StringField(required=True)
    params = db.DictField(required=True)
    transitions = db.ListField(db.DictField())


class Workflow(db.Document):
    steps = db.EmbeddedDocumentListField(Step)
    trigger = db.EmbeddedDocumentField(Trigger, required=True)
    # executions = db.ListField(db.ReferenceField(Execution))


class Execution(db.Document):
    TYPE_TRIGGER = 'trigger'
    TYPE_STEP = 'step'
    TYPES = (TYPE_TRIGGER, TYPE_STEP)

    workflow = db.StringField(required=True)
    name = db.StringField(required=True)
    type = db.StringField(choices=TYPES, required=True)
    result = db.DictField(required=True)

    @queryset_manager
    def latest(doc_cls, queryset):
        return queryset.order_by('-id').first()