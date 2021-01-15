import requests
from database.models import Execution, User
import datetime


def validate_account(workflow, step, user_id, pin):
    is_valid = User.objects(user_id=user_id, pin=pin).count() > 0
    print('validate_account')

    Execution(
        workflow=str(workflow.pk),
        name=step['id'],
        type=Execution.TYPE_STEP,
        result={'is_valid': is_valid}
    ).save()


def get_account_balance(workflow, step, user_id):
    user = User.objects(user_id=user_id).first()
    print('get_account_balance: ', float(user.balance))

    Execution(
        workflow=str(workflow.pk),
        name=step['id'],
        type=Execution.TYPE_STEP,
        result={'balance': float(user.balance)}
    ).save()


def deposit_money(workflow, step, user_id, money):
    print('deposit_money: ', money)
    user = User.objects(user_id=user_id).update_one(inc__balance=money)
    print(user)


def withdraw(workflow, step, user_id, money):
    print('withdraw: ', money)
    user = User.objects(user_id=user_id).update_one(inc__balance=money * -1)
    print(user)


def withdraw_in_dollars(workflow, step, user_id, money):
    print('deposit_money: ', money)
    print(datetime.date.today().isoformat())
    rate_params = {'vigenciadesde': datetime.date.today().isoformat()}
    rate = requests.get('https://www.datos.gov.co/resource/32sa-8pi3.json', params=rate_params)
    usd_rate = rate.json()[0]
    print(usd_rate)
    print(float(usd_rate['valor']) * money)

    user = User.objects(user_id=user_id).update_one(inc__balance=float(usd_rate['valor']) * money * -1)
    print(user)
