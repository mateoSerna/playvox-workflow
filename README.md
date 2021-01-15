# Playvox Workflow

## Tools
* Backend: Flask + mongodb

## Run stack

```bash
docker-compose -f docker-compose.yml up
```
Now you can see the services running:
* Backend: http://127.0.0.1:5000/

The endpoint to create a new user:
```bash
POST http://127.0.0.1:5000/users/
Sending the body in JSON format: {"user_id": "105398891", "pin": 2090}
```

The endpoint to list all users:
```bash
GET http://127.0.0.1:5000/users/
```

The endpoint to start a new workflow:
```bash
POST http://127.0.0.1:5000/workflow/
Sending the body in Multipart form: {"workflow": <workflow.json>}
```

To connect to the database:
```bash
* User: playvox
* DB: playvox
* Password: playvox
* Host: 127.0.0.1
* Port: 27017
```

To execute the tests:
```bash
$ python -m unittest
```
