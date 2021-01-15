import datetime

import requests
from database.models import Execution, User


def validate_account(workflow, step, user_id, pin):
    """Valída que la cuenta del usuario solicitado sea válida."""
    is_valid = User.objects(user_id=user_id, pin=pin).count() > 0
    print('Validación de cuenta de usuario: ', 'Válida' if is_valid else 'Inválida')

    Execution(
        workflow=str(workflow.pk),
        name=step['id'],
        type=Execution.TYPE_STEP,
        result={'is_valid': is_valid}
    ).save()


def get_account_balance(workflow, step, user_id):
    """Calcula el saldo actual del usaurio solicitado."""
    user = User.objects(user_id=user_id).first()
    print('Saldo actual del usuario: ', float(user.balance))

    Execution(
        workflow=str(workflow.pk),
        name=step['id'],
        type=Execution.TYPE_STEP,
        result={'balance': float(user.balance)}
    ).save()


def deposit_money(workflow, step, user_id, money):
    """Realiza un depósito de dinero en la cuenta del usuario solicitado."""
    User.objects(user_id=user_id).update_one(inc__balance=money)
    print('Cantidad depositada: ', money)


def withdraw(workflow, step, user_id, money):
    """Realiza un retiro de dinero de la cuenta del usuario solicitado."""
    User.objects(user_id=user_id).update_one(inc__balance=money * -1)
    print('Cantidad retirada: ', money)


def withdraw_in_dollars(workflow, step, user_id, money):
    """Realiza un retiro de dinero en dólares de la cuenta del usuario solicitado.
    Se consulta el endpoint de la entidad financiera para obtener la tasa de cambio actual.
    """
    rate_params = {'vigenciadesde': datetime.date.today().isoformat()}
    rate = requests.get('https://www.datos.gov.co/resource/32sa-8pi3.json', params=rate_params)
    usd_rate = rate.json()[0]

    print('Tasa de cambio: ', float(usd_rate['valor']))
    User.objects(user_id=user_id).update_one(inc__balance=float(usd_rate['valor']) * money * -1)
    print('Cantidad retirada: ', float(usd_rate['valor']) * money)
