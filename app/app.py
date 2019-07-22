from flask import Flask, request, send_from_directory, jsonify,render_template,send_file,current_app
from jsonschema.validators import extend
from pyshacl import validate
from jsonschema.validators import Draft4Validator
from jsonschema.exceptions import ValidationError
from jsonschema._utils import format_as_index
import json
import re
import codecs
import os
#os.chdir("./app")
import validate
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def homepage():
    return("JSON-LD Validator")

@app.route('/validatejson', methods=['POST'])
def jsonvalidate():

    result = {}
    print("REQUEST DATA IS:\n")
    print(request.data)
    if request.data == b'':
        return(jsonify({'error':"Please POST JSON file",'valid':False}))
    try:
        testjson = json.loads(request.data.decode('utf-8'))
    except:
        return(jsonify({'error':"Please POST JSON file",'valid':False}))

    if request.headers.get('Content-type') == "application/json-figshare":
        testjson = fig_to_schema(testjson)

    validator = validate.RDFSValidator(testjson)
    validator.validate()
    result['extra_elements'] = validator.extra_elements


    result['extra_elements'] = [x for x in result['extra_elements'] if x != "@context" and x != "@type" and x != "@id"]


    if validator.error == '':
        app.logger.info('%s passed schema validation', testjson.get('name'))
        schacl_validator = validate.ShaclValidator(testjson)
        schacl_validator.validate()

        if schacl_validator.valid:
            app.logger.info('%s passed shacl validation', testjson.get('name'))
            result['error'] = ''
            result['valid'] = True
            return(jsonify(result))

        else:
            app.logger.info('%s failed shacl validation', testjson.get('name'))
            result['error'] = schacl_validator.error
            result['valid'] = False
            return(jsonify(result))
    app.logger.info('%s failed schema validation', testjson.get('name'))
    result['error'] = validator.error
    result['valid'] = False
    return(jsonify(result))


@app.route('/swagger',methods = ['GET'])
def user_open_api():
    return send_file('static\\index.html')
    #return(index.html)


@app.route('/swagger.yaml',methods = ['GET'])
def open_api_yaml():
    return send_file('static\\openapi.yaml')
    #return(index.html)

def fig_to_schema(metadata):
    schema = {}
    if metadata.get('defined_type_name') == 'dataset':
        schema["@type"] = "Dataset"
    schema['url'] = []
    schema['url'].append(metadata.get('url'))
    schema['url'].append(metadata.get('url_private_html'))
    schema['url'].append(metadata.get('url_private_api'))
    schema['url'].append(metadata.get('url_public_api'))
    schema['url'].append(metadata.get('url_public_html'))
    if metadata.get('resource_title'):
        schema['name'] = metadata.get('resource_title')
    else:
        schema['name'] = metadata.get('title')
    if metadata.get('doi'):
        schema['doi'] = metadata['doi']
    schema['description'] = metadata.get('description')
    schema ['author'] = []
    for author in metadata.get('authors'):
        schema['author'].append(author.get('full_name'))
    schema['dateCreated'] = metadata.get('created_date')
    if metadata.get('citation'):
        schema['citation'] = metadata['citation']
    if metadata.get('files'):
        schema['distribution'] = []
        for file in metadata.get('files'):
            file_dict = {"@type":"DataDownload","name":file.get('name'),'contentUrl':file.get('download_url')}
            schema['distribution'].append(file_dict)

    return(schema)



if __name__=="__main__":
    app.run()
