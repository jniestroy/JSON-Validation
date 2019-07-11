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
os.chdir("./app")
import validate
import requests

app = Flask(__name__)


@app.route('/validatejson', methods=['POST'])
def jsonvalidate():
    
    result = {}

    testjson = request.get_json()

    if testjson is None:
        return(jsonify({'error':"Please POST JSON file",'valid':False}))

    validator = validate.RDFSValidator(testjson)
    validator.validate()
    result['extra_elements'] = validator.extra_elements
    

    result['extra_elements'] = [x for x in result['extra_elements'] if x != "@context" and x != "@type"]


    if validator.error == '':

        schacl_validator = validate.ShaclValidator(testjson)
        schacl_validator.validate()

        if schacl_validator.valid:
            result['error'] = ''
            result['valid'] = True
            return(jsonify(result))
        
        else:
            result['error'] = schacl_validator.error
            result['valid'] = False
            return(jsonify(result))
    result['error'] = validator.error
    result['valid'] = False
    return(jsonify(result))


# @app.route('/validatejson', methods=['POST'])
# def jsonvalidate():
#     testjson = request.get_json()

#     if testjson is None:
#         return(jsonify({'error':"Please POST JSON file",'valid':False}))

#     result = validate_json(testjson,"http://schema.org/",{'error': '','extra_elements':[]})


#     if result['error'] == '':

#         shacl_result = validate_shacl_min(testjson)

#         if shacl_result[0]:
#             result['valid'] = True
#             #result['error'] = result['error'] + shacl_result[1]
#             return(jsonify(result))
#         else:
#             result['error'] = result['error'] + shacl_result[1]
#     result['valid'] = False

#     return(jsonify(result))


@app.route('/swagger',methods = ['GET'])
def user_open_api():
    return send_file('static\\index.html')
    #return(index.html)


@app.route('/swagger.yaml',methods = ['GET'])
def open_api_yaml():
    return send_file('static\\openapi.yaml')
    #return(index.html)


if __name__=="__main__":
    app.run()
