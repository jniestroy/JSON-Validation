from flask import Flask, request, send_from_directory, jsonify
from jsonschema.validators import extend
from pyshacl import validate
from jsonschema.validators import Draft4Validator
from jsonschema.exceptions import ValidationError
from jsonschema._utils import format_as_index
import json
import re
import codecs
import requests 

app = Flask(__name__)

def validate_json(testjson,context,response = {'error': '','extra_elements':[]}):
    error = response['error']
    extra_elements = response['extra_elements']
    if '@type' not in testjson.keys():
        error = error +  " json missing type label"
        return({'error':error,'extra_elements':extra_elements})
    schema = get_schema(context,testjson['@type'])
    if schema == "Non-Valid Type":
        error = error + "Type not found on schema.org, "
        return({'error':error,'extra_elements':extra_elements})
    for element in testjson.keys():
        element_valid = 0
        element_seen = 0
        for prop in schema['@graph']:
            if element_seen:
                break
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
                    if validate_list(testjson[element],prop['schema:rangeIncludes'],context):
                        element_valid = True
                    else:
                        error = error + element + " in "+ testjson['@type'] +' at least an element in list is on improper type, ' 
                else:
                    if validate_element(testjson[element],prop['schema:rangeIncludes']):
                        element_valid = True
                    else:
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
def check_sub_class(prop_type,possible_types,context):
    schema = get_schema(context,prop_type)
    if schema == "Non-Valid Type":
        return False
    for prop in schema['@graph']:
        if prop['@id'] == "schema:" + prop_type:
            subclass = prop['rdfs:subClassOf']['@id']
            break
    if 'subclass' not in locals():
        return False
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
def validate_element(element,types):
    if isinstance(types,list):
        for valid_option in types:
            if isinstance(element,str):
                return True
            elif isinstance(element,list) and valid_option['@id'] == 'schema:Text':
                return True
            elif isinstance(element,str) and valid_option['@id'] == 'schema:URL':
                return True
            elif isinstance(element,str) and valid_option['@id'] == 'schema:Date':
                return True
            elif isinstance(element,str) and valid_option['@id'] == 'schema:Description':
                return True
            elif isinstance(element,str) and valid_option['@id'] == 'schema:Country':
                return True
            elif valid_option['@id'] == 'schema:Literal':
                return True
        return False
    else:
        if isinstance(element,str):
                return True
        elif isinstance(element,str) and types['@id'] == 'schema:URL':
                return True
        elif isinstance(element,str) and types['@id'] == 'schema:Date':
                return True
        elif isinstance(element,str) and types['@id'] == 'schema:Description':
                return True
        elif isinstance(element,str) and types['@id'] == 'schema:Country':
                return True
        elif isinstance(element,list):
                return True
        elif types['@id'] == 'schema:Literal':
                return True
        elif types['@id'] == 'schema:DataDownload':
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

def get_property(message):
    result = re.search("u''", message)
    return result.group(1)


def get_json(path):
    with open(path) as f:
        return json.load(f)


def recommended_draft4(validator, required, instance, schema):
    if not validator.is_type(instance, "object"):
        return
    for prop in required:
        if prop not in instance:
            yield ValidationError("%r is a recommended property" % prop)

Draft4ValidatorExtended = extend(
    validator=Draft4Validator,
    validators={u"recommended": recommended_draft4},
    version="draft4e"
)


def is_integer(text):
    try:
        int(text)
        return True
    except ValueError:
        return False


def validate_item(item):
    #file_name = SCHEMA_PATH + item['@type']#.rsplit('/', 1)[1]
    #schema = get_json(file_name + '.json')
    URL = "https://schema.org/"+ item['@type'] + ".jsonld?"
    req =  requests.get(url = URL)
    schema = req.json()
    instance = item#['properties']
    Draft4ValidatorExtended.check_schema(schema)
    validator = Draft4ValidatorExtended(schema)
    validation = {'minimum_missing': [], 'recommended_missing': [],
                  'bad_cardinality': [], 'bad_type': [], 'bad_cv': [], 'full_report': ''}
    for error in validator.iter_errors(instance):
        field = error.message.split("'")[1]
        if 'required' in error.message:
            validation['minimum_missing'].append(field)
            validation['full_report'] += '[MINIMUM ERROR] The missing ' + field + ' field is minimum' + '\n'
        elif 'recommended' in error.message:
            validation['recommended_missing'].append(field)
            validation['full_report'] += '[RECOMMENDED WARNING] The missing ' + field + ' field is recommended' + '\n'
        elif error.validator == 'oneOf':
            valid_types = []
            valid_cv = []
            for valid_schema in error.schema['oneOf']:
                if valid_schema['type'] != 'object':
                    valid_types.append(valid_schema['type'])
                    if 'enum' in valid_schema:
                        for valid_value in valid_schema['enum']:
                            valid_cv.append(valid_value)
                else:
                    if 'enum' in valid_schema['properties']['type']:
                        for valid_type in valid_schema['properties']['type']['enum']:
                            valid_types.append(valid_type)
            if isinstance(error.instance, list) and 'array' not in valid_types:
                validation['full_report'] += '[CARDINALITY ERROR] You must provide only one value for: '\
                                             + error.relative_path[0] + ' | Values found: ' + str(error.instance) + '\n'
                validation['bad_cardinality'].append(error.relative_path[0])
            elif 'integer' in valid_types and is_integer(error.instance):
                continue
            else:
                if 'array' in valid_types:
                    valid_types.remove('array')
                if valid_cv:
                    valid_cv = list(set(valid_cv))
                    validation['bad_cv'].append(error.relative_path[0])
                    validation['full_report'] += '[CONTROLLED VOCABULARY ERROR] The value for '\
                                                 + error.relative_path[0] +\
                                                 ' is not in the Controlled Vocabulary: [' + ', '.join(valid_cv) + '] '
                    validation['full_report'] += '| Value found: ' + str(error.instance) + '\n'
                else:
                    validation['bad_type'].append(error.relative_path[0])
                    validation['full_report'] += '[TYPE ERROR] One of the ' + error.relative_path[0] +\
                                                 ' values is not any of the valid types: ' \
                                                 '[' + ', '.join(valid_types) + '] '
                    validation['full_report'] += '| Value found: ' + str(error.instance) + '\n'
    return validation

def validate_shacl_min(testjson):
    testjson = json.dumps(testjson)
    shapes_file = '''
    @prefix dash: <http://datashapes.org/dash#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix schema: <http://schema.org/> .
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    schema:DatasetShape
        a sh:NodeShape ;
        sh:targetClass schema:Dataset ;
        sh:property [
            sh:path schema:name ;
            sh:datatype xsd:string ;
            sh:name "dataset name" ;
            sh:minCount 1 ;
        ] ;
        sh:property [
            sh:path schema:description ;
            sh:datatype xsd:string ;
            sh:name "dataset description" ;
            sh:minCount 1 ;
        ] ;
        sh:property [
            sh:path schema:author ;
            sh:node schema:AuthorShape ;
            sh:minCount 1 ;
        ] ;
        sh:property [
            sh:path schema:dateCreated ;
            sh:minCount 1 ;
        ] .
    schema:AuthorShape 
        a sh:NodeShape ;
        sh:targetClass schema:Author ;
        sh:property [
            sh:path schema:url ;
            sh:minCount 1;
        ] ;
        sh:property [
            sh:path schema:name ;
            sh:datatype xsd:string ;
            sh:minCount 1;
        ] .
    schema:PersonShape
        a sh:NodeShape ;
        sh:targetClass schema:Person ;
        sh:property [
            sh:path schema:name ;
            sh:datatype xsd:string ;
            sh:minCount 1 ;
        ] ;
        sh:property [
            sh:path schema:email ;
            sh:datatype xsd:string ;
        ] .
    schema:DataCatalogShape
        a sh:NodeShape ;
        sh:targetClass schema:DataCatalog ;
        sh:property [
            sh:path schema:dataset ;
            sh:node schema:DatasetShape ;
        ].
    '''
    shapes_file_format = 'turtle'
    data_file_format = 'json-ld'
    conforms, v_graph, v_text = validate(testjson, shacl_graph=shapes_file,
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
    print(result)
    if result['error'] == '':
        shacl_result = validate_shacl_min(testjson)
        if shacl_result[0]:
            result['valid'] = True
            return(jsonify(result))
        else:
            result['error'] = result['error'] + shacl_result[1]
    result['valid'] = False
    
    return(jsonify(result))

@app.route('/help',methods = ['GET'])
def print_documentation():
    print("hi")
    return "hi"
    return send_from_directory('','index.html')
    #return(index.html)

if __name__=="__main__":
    app.run()
    