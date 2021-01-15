import datetime

import requests
from flask import abort

from database.models import Execution, User


class BankService:
    def __init__(self, workflow):
        """Inicializa la instancia del servicio Bank."""
        self.workflow = workflow

    def call_action(self, action, params):
        """Ejecuta una acción (método) implementada dentro de la clase."""
        try:
            getattr(self, action)(**params)
        except AttributeError:
            abort(405, description=f'Metodo {action} no soportado.')
        except Exception:
            abort(500, description=f'Error ejecutando método o método no soportado {action}.')

    def validate_account(self, step, user_id, pin):
        """Valída que la cuenta del usuario solicitado sea válida."""
        is_valid = User.objects(user_id=user_id, pin=pin).count() > 0
        print('Validación de cuenta de usuario: ', 'Válida' if is_valid else 'Inválida')

        Execution(
            workflow=str(self.workflow.pk),
            name=step['id'],
            type=Execution.TYPE_STEP,
            result={'is_valid': is_valid}
        ).save()

    def get_account_balance(self, step, user_id):
        """Calcula el saldo actual del usaurio solicitado."""
        user = User.objects(user_id=user_id).first()
        print('Saldo actual del usuario: ', float(user.balance))

        Execution(
            workflow=str(self.workflow.pk),
            name='account_balance',
            type=Execution.TYPE_STEP,
            result={'balance': float(user.balance)}
        ).save()

    def deposit_money(self, step, user_id, money):
        """Realiza un depósito de dinero en la cuenta del usuario solicitado."""
        if money >= 0:
            print('Cantidad depositada: ', money)
            User.objects(user_id=user_id).update_one(inc__balance=money)
        else:
            print('No es posible depositar valores negativos.')

    def withdraw(self, step, user_id, money):
        """Realiza un retiro de dinero de la cuenta del usuario solicitado."""
        user = User.objects(user_id=user_id).first()

        if money > 0:
            if user.balance >= money:
                print('Cantidad retirada: ', money)
                user.balance = float(user.balance) - float(money)
                user.save()
            else:
                print('No hay fondos suficientes para realizar el retiro.')
        else:
            print('No es posible retirar valores negativos.')

    def withdraw_in_dollars(self, step, user_id, money):
        """Realiza un retiro de dinero en dólares de la cuenta del usuario solicitado.
        Se consulta el endpoint de la entidad financiera para obtener la tasa de cambio actual.
        """
        rate_params = {'vigenciadesde': datetime.date.today().isoformat()}
        rate = requests.get('https://www.datos.gov.co/resource/32sa-8pi3.json', params=rate_params)
        usd_rate = float(rate.json()[0]['valor'])

        print('Tasa de cambio: ', usd_rate)
        user = User.objects(user_id=user_id).first()

        if money > 0:
            if user.balance >= (usd_rate * money):
                print('Cantidad retirada: ', usd_rate * money)
                user.balance = float(user.balance) - (usd_rate * money)
                user.save()
            else:
                print('No hay fondos suficientes para realizar el retiro.')
        else:
            print('No es posible retirar valores negativos.')
