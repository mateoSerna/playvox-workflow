from database.models import Execution
from flask import abort
from services import bank


def execute_trigger(workflow):
    """Realiza la ejecución del trigger del workflow."""
    print('Inicia ejecución del Trigger...')

    try:
        trigger = workflow.trigger
        Execution(
            workflow=str(workflow.pk),
            name=trigger.id,
            type=Execution.TYPE_TRIGGER,
            result=trigger.params
        ).save()
    except Exception:
        abort(500, description='Error ejecutando Trigger.')

    if trigger.transitions:
        execute_transitions(workflow=workflow, transitions=trigger.transitions)


def execute_transitions(workflow, transitions):
    """Ejecuta cada transicion hacia un paso verificando que las condiciones de la transicion se cumplan."""
    target = None
    for transition in transitions:
        print(f'Inicia ejecución de la transicion hacia el paso {transition["target"]}')

        if transition['condition']:
            for condition in transition['condition']:
                print('Validando condicion de la transicion:')

                try:
                    _filter = f'result__{condition["field_id"]}'
                    _filter += f'__{condition["operator"]}' if not condition['operator'] == 'eq' else ''

                    filters = {'workflow': str(workflow.pk), 'name': condition['from_id']}
                    filters[_filter] = condition['value']
                except Exception:
                    abort(
                        500,
                        description=f'Error calculando filtros de una condicion hacia el paso {transition["target"]}'
                    )

                if Execution.objects(**filters):
                    target = transition['target']
                    break
            if target:
                break
        else:
            target = transition['target']
            break

    if target:
        execute_step(workflow=workflow, target=transition['target'])


def execute_step(workflow, target):
    """Ejecuta la accion dentro de un paso y posteriormente continúa hacia otra transición si existe."""
    step = workflow.steps.get(id=target)
    print(f'Inicia ejecución del paso {step["id"]}')

    print('Inicia obtención de los parámetros del paso')
    params = {'workflow': workflow, 'step': step}
    for param_name, param_value in step['params'].items():
        try:
            params[param_name] = get_param(workflow=workflow, param=param_value)
        except Exception:
            abort(500, description='Error obteniendo parámetro para la ejecución del paso.')

    try:
        getattr(bank, step['action'])(**params)
    except AttributeError:
        abort(405, description=f'Metodo {step["action"]} no soportado.')

    if step.transitions:
        execute_transitions(workflow=workflow, transitions=step.transitions)


def get_param(workflow, param):
    """Obtiene el parametro solicitado para la ejecución de un paso."""
    return_param = None

    try:
        if param['from_id']:
            execution = Execution.objects(workflow=str(workflow.pk), name=param['from_id']).order_by('-id').first()
            return_param = execution.result[param['param_id']]
        elif param['value']:
            return_param = param['value']
    except Exception:
        abort(500, description=f'Error obtiendo el parámetro {param["param_id"]}.')

    return return_param
