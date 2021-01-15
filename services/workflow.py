from database.models import Execution, Step, Trigger, Workflow
from flask import abort
from services.bank import BankService


class WorkflowService:
    def __init__(self, data):
        """Inicializa la instancia del servicio Workflow."""
        self.workflow = self.create_workflow(data=data)
        self.bank = BankService(workflow=self.workflow)

        self.execute_trigger()

    def create_workflow(self, data):
        """Inicia el workflow automatizado."""
        try:
            trigger = Trigger(**data['trigger'])
            workflow = Workflow(trigger=trigger).save()

            for data_step in data['steps']:
                step = Step(**data_step)
                workflow.steps.append(step)
                workflow.save()
        except Exception:
            abort(500, description='Error procesando el archivo, por favor intente de nuevo.')

        return workflow

    def execute_trigger(self):
        """Realiza la ejecución del trigger del workflow."""
        print('Inicia ejecución del Trigger...')

        try:
            trigger = self.workflow.trigger
            Execution(
                workflow=str(self.workflow.pk),
                name=trigger.id,
                type=Execution.TYPE_TRIGGER,
                result=trigger.params
            ).save()
        except Exception:
            abort(500, description='Error ejecutando Trigger.')

        if trigger.transitions:
            self.execute_transitions(transitions=trigger.transitions)

    def execute_transitions(self, transitions):
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

                        filters = {'workflow': str(self.workflow.pk), 'name': condition['from_id']}
                        filters[_filter] = condition['value']
                    except Exception:
                        abort(
                            500,
                            description=(
                                f'Error calculando filtros de una condicion hacia el paso {transition["target"]}'
                            )
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
            self.execute_step(target=transition['target'])

    def execute_step(self, target):
        """Ejecuta la accion dentro de un paso y posteriormente continúa hacia otra transición si existe."""
        step = self.workflow.steps.get(id=target)
        print(f'Inicia ejecución del paso {step["id"]}')

        print('Inicia obtención de los parámetros del paso')
        params = {'step': step}
        for param_name, param_value in step['params'].items():
            try:
                params[param_name] = self.get_param(param=param_value)
            except Exception:
                abort(500, description='Error obteniendo parámetro para la ejecución del paso.')

        self.bank.call_action(action=step['action'], params=params)

        if step.transitions:
            self.execute_transitions(transitions=step.transitions)

    def get_param(self, param):
        """Obtiene el parámetro solicitado para la ejecución de un paso."""
        return_param = None

        try:
            if param['from_id']:
                execution = (
                    Execution
                    .objects(workflow=str(self.workflow.pk), name=param['from_id'])
                    .order_by('-id')
                    .first()
                )

                return_param = execution.result[param['param_id']]
            elif param['value']:
                return_param = param['value']
        except Exception:
            abort(500, description=f'Error obtiendo el parámetro {param["param_id"]}.')

        return return_param
