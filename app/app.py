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
import requests 

app = Flask(__name__)


def validate_json(testjson,context,response = {'error': '','extra_elements':[]}):
    error = response['error']
    extra_elements = response['extra_elements']
    if '@type' not in testjson.keys():
        error = error +  " json missing type label, "
        return({'error':error,'extra_elements':extra_elements})
    schema = get_schema(context,testjson['@type'])
    if schema == "Non-Valid Type":
        error = error + testjson["@type"] +" not found on schema.org, "
        return({'error':error,'extra_elements':extra_elements})
    for element in testjson.keys():
        element_seen = False
        #Loops through provided schema to see if property in json is in proveded schema
        for prop in schema['@graph']:
            if element_seen:
                break
            #if property in json is in schema validate that provided information matches schema requirements
            if prop['@id'] == "schema:" +element:
                element_seen = True
                if isinstance(testjson[element],dict):
                    if valid_type(testjson[element],prop['schema:rangeIncludes'],context):
                        result = validate_json(testjson[element],context,response)
                        error = error + result['error']
                        extra_elements = extra_elements + result['extra_elements']
                    else:
                        error = error + element + ' is missing type or has type outside of range of ' + str(prop['schema:rangeIncludes']) + ', '
                elif isinstance(testjson[element],list):
                    if not validate_list(testjson[element],prop['schema:rangeIncludes'],context):
                        error = error + element + " in "+ testjson['@type'] +' at least an element in list is on improper type, ' 
                else:
                    if not validate_element(testjson[element],prop['schema:rangeIncludes']):
                        error = error + element + " in "+ testjson['@type'] + " is of wrong typeshould be in " + str(prop['schema:rangeIncludes']) + ', '
        if not element_seen:
                extra_elements.append(element)
    extra_elements = set(extra_elements)
    extra_elements = list(extra_elements)
    if '@context' in extra_elements:
        extra_elements.remove('@context')
    if '@type' in extra_elements:
        extra_elements.remove('@type')
    return({'error':error,'extra_elements':extra_elements})
def valid_type(testjson,types,context):
    if '@type' not in testjson.keys():
        return False
    if isinstance(types,list):
        possible_types = []
        for element in types:
            possible_types.append(element['@id'])
    else:
        possible_types = [types['@id']]
    if 'schema:' + testjson['@type'] in possible_types:
        return True
    elif check_sub_class(testjson['@type'],possible_types,context):
        return True
    return False
#Checks if given type is sub-class of possible types
def check_sub_class(prop_type,possible_types,context):
    schema = get_schema(context,prop_type)
    if schema == "Non-Valid Type":
        return False
    #Grabs desired subclass information from schema.org about property we're interested in
    for prop in schema['@graph']:
        if prop['@id'] == "schema:" + prop_type:
            subclass = prop['rdfs:subClassOf']['@id']
            break
    #subClass variable doesn't exsist means that the propety is not a subclass of anything so 
    #not a subclass of any test types so false
    if 'subclass' not in locals():
        return False
    #if the propety is a subclass of one of the possible types then return true
    if subclass in possible_types:
        return True
    return False
def validate_list(test_list,types,context):
    valid_list = True
    if isinstance(types,list):
        possible_types = []
        for element in types:
            possible_types.append(element['@id'])
    else:
        possible_types = [types['@id']]
    for allowed_type in possible_types:
        for element in test_list:
            if isinstance(element,dict):
                dict_type = {'@id':allowed_type}
                if valid_type(element,dict_type,context):
                    if validate_json(element,context)['error'] == '':
                        test = 1
                    else:
                        valid_list = 0
                else:
                    valid_list = 0
            else:
                dict_type = {'@id':allowed_type}
                if not validate_element(element,dict_type):
                    valid_list = 0
        if valid_list:
            return True
    return False
#element is the value of interest types is dictionary where allowed types is either list of dictionaries or
#single dictionary, the types are held in the @id key of each dictionary
def validate_element(element,types):
    if isinstance(types,list):
        for valid_option in types:
            if isinstance(element,str):#Assume if they've given a string its correct
                return True
            elif isinstance(element,int) and valid_option['@id'] == 'schema:Number':
                return True
        return False
    else:
        if isinstance(element,str):
                return True
        elif isinstance(element,int) and types['@id'] == 'schema:Number':
                return True
        else:
            return False
def get_schema(context,prop_type):
    url = context + prop_type + ".jsonld"
    if prop_type == "Taxon":
        schema = dict()
        schema['@graph'] = [{"@id":"schema:name","@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:Text"}},{"@id":"schema:parentTaxon" "schema:","@type": "rdf:Property","schema:rangeIncludes": [{"@id": "schema:Text"},{"@id": "schema:Taxon"}]}]
        schema['@graph'].append({"@id":"schema:taxonRank","@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:Text"}})
        schema['@graph'].append({"@id":"schema:url" ,"@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:Text"}})
        return(schema)
    r = requests.get(url) 
    if r.status_code == 200:
        schema = r.json()
        if prop_type == 'Dataset':
            schema['@graph'].append({"@id":"schema:measurementTechnique","@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:Text"}})
            schema['@graph'].append({"@id":"schema:variableMeasured","@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:Text"}})
        if prop_type == 'Event':
            schema['@graph'].append({"@id":"schema:contact","@type": "rdf:Property","schema:rangeIncludes": [{"@id": "schema:Organization"},{"@id": "schema:Person"}]})
            schema['@graph'].append({"@id":"schema:eventType","@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:Text"}})
            schema['@graph'].append({"@id":"schema:audience","@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:URL"}})
            schema['@graph'].append({"@id":"schema:deadline","@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:Text"}})
            schema['@graph'].append({"@id":"schema:hostInstitution","@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:Orginzation"}})
            schema['@graph'].append({"@id":"schema:eligibility","@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:Text"}})
            schema['@graph'].append({"@id":"schema:prerequisite","@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:Text"}})
            schema['@graph'].append({"@id":"schema:socialMedia","@type": "rdf:Property","schema:rangeIncludes": {"@id": "URL"}})
            schema['@graph'].append({"@id":"schema:registrationStatus","@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:Text"}})
            schema['@graph'].append({"@id":"schema:topic","@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:URL"}})
            schema['@graph'].append({"@id":"schema:accreditation","@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:Orginzation"}})
        if prop_type == "TrainingMaterial":
            schema['@graph'].append({"@id":"schema:difficultyLevel","@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:Text"}})
            schema['@graph'].append({"@id":"schema:pid","@type": "rdf:Property","schema:rangeIncludes": {"@id": "schema:Text"}})
        return(schema)
    else:
        return("Non-Valid Type")
def validate_shacl_min(testjson):
    testjson = json.dumps(testjson)
    #need app// in front below to work locally
    f = open("./schema definitions/shacl definitions.txt", "r")
    shapes_file = f.read()
    shapes_file_format = 'turtle'
    data_file_format = 'json-ld'
    conforms, _, v_text = validate(testjson, shacl_graph=shapes_file,
                                     data_graph_format=data_file_format,
                                     shacl_graph_format=shapes_file_format,
                                     inference='rdfs', debug=True,
                                     serialize_report_graph=True)
    return(conforms,v_text)



@app.route('/validatejson', methods=['POST'])
def jsonvalidate():
    testjson = request.get_json()
    if testjson is None:
        return(jsonify({'error':"Please POST JSON file",'valid':False}))
    result = validate_json(testjson,"http://schema.org/",{'error': '','extra_elements':[]})
    if result['error'] == '':
        shacl_result = validate_shacl_min(testjson)
        if shacl_result[0]:
            result['valid'] = True
            return(jsonify(result))
        else:
            result['error'] = result['error'] + shacl_result[1]
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

if __name__=="__main__":
    app.run()
    