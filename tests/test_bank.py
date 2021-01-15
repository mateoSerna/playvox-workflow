import unittest
from unittest.mock import Mock

from mongoengine import connect, disconnect

from database.models import Execution, User
from services.bank import BankService


class TestBank(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.connection = connect(db='mongoenginetest', host='mongomock://localhost')
        self.user_id = '1088308123'

        user = User(user_id=self.user_id, pin='12345')
        user.save()

    @classmethod
    def tearDownClass(self):
        self.connection.drop_database('mongoenginetest')
        disconnect()

    def setUp(self):
        User.objects(user_id=self.user_id).update_one(balance=0)
        Execution.objects().all().delete()

    def test_validate_account(self):
        """Prueba que valída el método de validar usuario."""
        user = User.objects().first()
        self.assertEqual(user.user_id, self.user_id)
        self.assertEqual(user.pin, 12345)
        self.assertNotEqual(user.pin, '12345')

    def test_deposit_money(self):
        """Prueba que valída el método de depositar dinero en la cuenta de un usuario exitosamente."""
        mock_workflow = Mock(pk=12345)
        user = User.objects().first()
        money = 100000

        bank = BankService(workflow=mock_workflow)
        bank.deposit_money(step=None, user_id=user.user_id, money=money)
        bank.get_account_balance(step=None, user_id=user.user_id)

        execution = Execution.objects(workflow=str(mock_workflow.pk)).first()
        self.assertEqual(execution.result['balance'], money)

    def test_deposit_money_negative(self):
        """Prueba que valída el método de depositar dinero en la cuenta de un usuario con valores negativos."""
        mock_workflow = Mock(pk=12345)
        user = User.objects().first()
        money = -100000

        bank = BankService(workflow=mock_workflow)
        bank.deposit_money(step=None, user_id=user.user_id, money=money)
        bank.get_account_balance(step=None, user_id=user.user_id)

        execution = Execution.objects(workflow=str(mock_workflow.pk)).first()
        self.assertEqual(execution.result['balance'], 0)

    def test_withdraw(self):
        """Prueba que valída el método de retirar dinero de la cuenta de un usuario exitosamente."""
        mock_workflow = Mock(pk=12345)
        user = User.objects().first()
        money = 100000
        withdraw = 90000

        bank = BankService(workflow=mock_workflow)
        bank.deposit_money(step=None, user_id=user.user_id, money=money)
        bank.withdraw(step=None, user_id=user.user_id, money=withdraw)
        bank.get_account_balance(step=None, user_id=user.user_id)

        execution = Execution.objects(workflow=str(mock_workflow.pk)).first()
        self.assertEqual(execution.result['balance'], money - withdraw)

    def test_withdraw_negative(self):
        """Prueba que valída el método de retirar dinero de la cuenta de un usuario con valores negativos."""
        mock_workflow = Mock(pk=12345)
        user = User.objects().first()
        money = 100000
        withdraw = -90000

        bank = BankService(workflow=mock_workflow)
        bank.deposit_money(step=None, user_id=user.user_id, money=money)
        bank.withdraw(step=None, user_id=user.user_id, money=withdraw)
        bank.get_account_balance(step=None, user_id=user.user_id)

        execution = Execution.objects(workflow=str(mock_workflow.pk)).first()
        self.assertEqual(execution.result['balance'], money)

    def test_withdraw_no_funds(self):
        """Prueba que valída el método de retirar dinero de la cuenta de un usuario sin fondos suficientes."""
        mock_workflow = Mock(pk=12345)
        user = User.objects().first()
        money = 200000
        withdraw = 300000

        bank = BankService(workflow=mock_workflow)
        bank.deposit_money(step=None, user_id=user.user_id, money=money)
        bank.withdraw(step=None, user_id=user.user_id, money=withdraw)
        bank.get_account_balance(step=None, user_id=user.user_id)

        execution = Execution.objects(workflow=str(mock_workflow.pk)).first()
        self.assertEqual(execution.result['balance'], money)
