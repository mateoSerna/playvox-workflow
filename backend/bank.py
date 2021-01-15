from database.models import Execution, User


def validate_account(workflow, step, user_id, pin):
    is_valid = User.objects(user_id=user_id, pin=pin).count() > 0

    execution = Execution(
        workflow=str(workflow.pk),
        name=step['id'],
        type=Execution.TYPE_STEP,
        result={'is_valid': is_valid}
    ).save()
