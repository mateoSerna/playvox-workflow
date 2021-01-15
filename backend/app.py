from database.db import initialize_db
from database.models import Step, Trigger, User, Workflow
from flask import Flask, Response, abort, json, request
from services.workflow import execute_trigger

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://playvox:playvox@playvox-database/playvox'
}

initialize_db(app)


@app.route('/users/')
def get_users():
    """Retorna los usuarios creados en el sistema."""
    users = User.objects().to_json()
    return Response(users, mimetype="application/json", status=200)


@app.route('/users/', methods=['POST'])
def save_user():
    """Guarda un usuario nuevo en el sistema"""
    body = request.get_json()
    user = User(**body).save()
    return {'id': str(user.id)}, 200


@app.route('/workflow/', methods=['POST'])
def workflow():
    """Inicia el proceso automatizado del workflow.
    Recibe un archivo JSON que debe cumplir con una estructura definida.
    """
    filename = 'workflow'
    if filename not in request.files:
        abort(400, description='El archivo workflow.json no ha sido enviado.')

    try:
        workflow_file = request.files[filename].read()
        data = json.loads(workflow_file.decode('utf8').replace("'", '"'))
    except Exception:
        abort(500, description='Error leyendo el archivo, por favor verifique el contenido e intente de nuevo.')

    try:
        trigger = Trigger(**data['trigger'])
        workflow = Workflow(trigger=trigger).save()

        for data_step in data['steps']:
            step = Step(**data_step)
            workflow.steps.append(step)
            workflow.save()
    except Exception:
        abort(500, description='Error procesando el archivo, por favor intente de nuevo.')

    execute_trigger(workflow=workflow)
    print('Se ha finalizado la ejecución del workflow correctamente.')

    return {'detalle': 'Se ha finalizado la ejecución del workflow correctamente.'}


app.run(debug=True, host='0.0.0.0')
