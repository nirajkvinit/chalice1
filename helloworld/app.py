import json
import boto3
from botocore.exceptions import ClientError
from chalice import Chalice
from chalice import BadRequestError, NotFoundError

app = Chalice(app_name='helloworld')
app.debug = True

S3 = boto3.client('s3', region_name="us-east-2")
BUCKET = "pyhashcloud"

CITIES_TO_STATE = {
    'seattle': 'WA',
    'portland': 'OR',
}

OBJECTS = {}


@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/cities/{city}')
def state_of_city(city):
    try:
        return {'state': CITIES_TO_STATE[city]}
    except KeyError:
        raise BadRequestError("Unknown city '%s', valid choices are: %s" % (
            city, ', '.join(CITIES_TO_STATE.keys())))


@app.route("/resource/{value}", methods=['PUT', 'POST'])
def put_test(value):
    return {"value": value}


@app.route('/objects/{key}', methods=["GET", "PUT"])
def myobject(key):
    request = app.current_request
    if request.method == 'PUT':
        OBJECTS[key] = request.json_body
        return OBJECTS
    elif request.method == 'GET':
        try:
            return {key: OBJECTS[key]}
        except KeyError:
            raise NotFoundError(key)


@app.route('/objects2/{key}', methods=['GET', 'PUT', 'POST'])
def s3objects(key):
    request = app.current_request
    if request.method in ('PUT', 'POST'):
        S3.put_object(Bucket=BUCKET, Key=key,
                      Body=json.dumps(request.json_body))
    elif request.method == 'GET':
        try:
            response = S3.get_object(Bucket=BUCKET, Key=key)
            return json.loads(response['Body'].read())
        except ClientError as e:
            raise NotFoundError(key)
