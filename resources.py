from flask import Response, abort, json, request
from flask_restful import Resource
from mongoengine.errors import NotUniqueError

from database.models import User
from services.workflow import WorkflowService


class WorkflowResource(Resource):
    """Administra la ejecución y control de un Workflow"""

    def post(self):
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

        WorkflowService(data=data)
        print('Se ha finalizado la ejecución del workflow correctamente.')

        return {'detail': 'Se ha finalizado la ejecución del workflow correctamente.'}


class UsersResource(Resource):
    """Administra el recurso de Usuario."""

    def get(self):
        """Retorna los usuarios creados en el sistema."""
        users = User.objects().to_json()
        return Response(users, mimetype='application/json')

    def post(self):
        """Guarda un usuario nuevo en el sistema"""
        response = {}

        try:
            body = request.get_json()
            user = User(**body).save()

            response = {'detail': str(user.user_id), 'code': 200}
        except NotUniqueError:
            response = {'detail': 'Este usuario ya exíste.', 'code': 400}
        except Exception:
            response = {'detail': 'No fue posible crear el usuario. Intente nuevamente.', 'code': 500}

        return {'detail': response['detail']}, response['code']
