import bank

from flask import Flask, json, request, Response
from database.db import initialize_db
from database.models import Execution, User, Workflow, Step, Trigger


app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://playvox:playvox@playvox-database/playvox'
}

initialize_db(app)


@app.route('/users')
def get_users():
    users = User.objects().to_json()
    return Response(users, mimetype="application/json", status=200)


@app.route('/users', methods=['POST'])
def save_user():
    body = request.get_json()
    user = User(**body).save()
    return {'id': str(user.id)}, 200


@app.route('/workflow')
def workflow():
    json_data = open('./workflow.json')
    data = json.load(json_data)
    print(data['trigger'])

    trigger = Trigger(**data['trigger'])
    workflow = Workflow(trigger=trigger).save()

    for data_step in data['steps']:
        step = Step(**data_step)
        workflow.steps.append(step)
        workflow.save()

    workflow = Workflow.objects().order_by('-id').first()
    print(workflow.to_json())
    print('*'*10)
    execute_trigger(workflow=workflow)


def execute_trigger(workflow):
    print(workflow.trigger.to_json())
    trigger = workflow.trigger
    execution = (
        Execution(
            workflow=str(workflow.pk),
            name=trigger.id,
            type=Execution.TYPE_TRIGGER,
            result=trigger.params
        )
        .save()
    )

    print('execution: ', execution.to_json())

    if trigger.transitions:
        execute_transitions(workflow=workflow, transitions=trigger.transitions)


def execute_step(workflow, target):
    print('target: ', target)
    step = workflow.steps.get(id=target)
    print('step: ', step.to_json())

    params = {'workflow': workflow, 'step': step}
    for param_name, param_value in step['params'].items():
        params[param_name] = get_param(workflow=workflow, param=param_value)

    getattr(bank, step['action'])(**params)

    if step.transitions:
        execute_transitions(workflow=workflow, transitions=step.transitions)


def execute_transitions(workflow, transitions):
    for transition in transitions:
        print('transition: ', transition)
        if transition['condition']:
            for condition in transition['condition']:
                print('nueva condicion: ')
                _filter = f'result__{condition["field_id"]}'
                _filter += f'__{condition["operator"]}' if not condition['operator'] == 'eq' else ''

                filters = {'workflow': str(workflow.pk), 'name': condition['from_id']}
                filters[_filter] = condition['value']
                print('filters: ', filters)

                if Execution.objects(**filters):
                    execute_step(workflow=workflow, target=transition['target'])
                    break
        else:
            execute_step(workflow=workflow, target=transition['target'])


def get_param(workflow, param):
    return_param = None
    print('workflow id: ', str(workflow.pk))
    if param['from_id']:
        execution = Execution.objects(workflow=str(workflow.pk), name=param['from_id']).order_by('-id').first()
        return_param = execution.result[param['param_id']]
        print('execution: ', execution.to_json())
    elif param['value']:
        return_param = param['value']

    return return_param


app.run(debug=True, host='0.0.0.0')
