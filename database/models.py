from .db import db


class User(db.Document):
    """Representa un Usuario en el sistema"""
    user_id = db.StringField(required=True, unique=True)
    pin = db.IntField(required=True)
    balance = db.DecimalField(required=True, default=0)


class Step(db.EmbeddedDocument):
    """Representa un Paso en el sistema"""
    id = db.StringField(required=True)
    params = db.DictField(required=True)
    action = db.StringField(required=True)
    transitions = db.ListField(db.DictField())


class Trigger(db.EmbeddedDocument):
    """Representa un Trigger en el sistema"""
    id = db.StringField(required=True)
    params = db.DictField(required=True)
    transitions = db.ListField(db.DictField())


class Workflow(db.Document):
    """Representa un Workflow en el sistema, relaciona el conjunto de Paso y el Trigger."""
    steps = db.EmbeddedDocumentListField(Step)
    trigger = db.EmbeddedDocumentField(Trigger, required=True)


class Execution(db.Document):
    """Representa la Ejecución de un Paso almacenando el resultado."""
    TYPE_TRIGGER = 'trigger'
    TYPE_STEP = 'step'
    TYPES = (TYPE_TRIGGER, TYPE_STEP)

    workflow = db.StringField(required=True)
    name = db.StringField(required=True)
    type = db.StringField(choices=TYPES, required=True)
    result = db.DictField(required=True)
