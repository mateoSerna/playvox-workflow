from database.models import Execution, User


def validate_account(workflow, step, user_id, pin):
    is_valid = User.objects(user_id=user_id, pin=pin).count() > 0
    print('validate_account')

    execution = Execution(
        workflow=str(workflow.pk),
        name=step['id'],
        type=Execution.TYPE_STEP,
        result={'is_valid': is_valid}
    ).save()


def get_account_balance(workflow, step, user_id):
    user = User.objects(user_id=user_id).first()
    print('get_account_balance')

    execution = Execution(
        workflow=str(workflow.pk),
        name=step['id'],
        type=Execution.TYPE_STEP,
        result={'balance': float(user.balance)}
    ).save()
