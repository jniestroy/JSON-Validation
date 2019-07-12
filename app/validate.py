import rdflib
import json
import requests
from pyshacl import validate
import os

# class Validator(object):

#     def __init__(self, data):
#         pass

#     def validate_jsonschema(self):
#         return

#     def validate_shacl(self):
#         return

# class JsonSchemaValidator(object):

#     def __init__(self):
#         pass



class RDFSValidator(object):

    def __init__(self, data,path = "./static/"):
    #""" Set up RDFSValidator class, read in json-ld to validate, open RDFS definition file and parse into ...
    #"""
        with open(path + "schema.jsonld", "rb") as file:
            schema_rdfs = json.loads(file.read())

        self.g = rdflib.Graph().parse(data = json.dumps(schema_rdfs.get("@graph")),context=schema_rdfs.get("@context"), format="json-ld")

        classes = [ elem.get("@id") for elem in schema_rdfs['@graph'] if elem.get("@type") == "rdfs:Class" ]
        properties = [ elem.get("@id") for elem in schema_rdfs['@graph'] if elem.get("@type") == "rdf:Property" ]

        #self.schema = { elem.get("@id"): elem for elem in schema_rdfs}
        self.context = "http://schema.org/"
        self.error = ""
        self.extra_elements = []
        self.data = data


        #Creates list of all properites for each class
        #including those which are inherited from classes above
        self.schema_properties = {}
        for clas in classes:
            self.schema_properties[clas] = []

            superClasses = [f for f in self.g.transitive_objects(
                rdflib.term.URIRef(clas),
                rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'))]

            for superClass in superClasses:

                self.schema_properties[clas].extend([str(found) for found in self.g.transitive_subjects(
                                                                            rdflib.term.URIRef("http://schema.org/domainIncludes"),
                                                                            rdflib.term.URIRef(superClass))])

        #Gathers acceptable ranges for all properties found
        self.schema_property_ranges = {}
        for prop in properties:
            self.schema_property_ranges[prop] = [str(f) for f in self.g.transitive_objects(
                                                                rdflib.term.URIRef(prop),
                                                                rdflib.term.URIRef("http://schema.org/rangeIncludes"))]
    #Validates given json-ld
    def validate(self):

        if not self.initial_validate(self.data,"JSON"):
            return

        self.parse(self.data,"JSON")

        return


    #Checks that json meets minimum requirements for validation
    # 1.) json is a dictionary
    # 2.) json contains @type tag
    # 3.) the type submitted is recongized by the vocab
    def initial_validate(self,data,element):

        if not isinstance(data,dict):
            self.error += " " + element + " not of type dict."
            return False

        elif '@type' not in data.keys():
            self.error += " " + element + " missing required property @type."
            return False

        elif self.context + data['@type'] not in self.schema_properties.keys():
            self.error += " " + element + " not of reconginized class."
            return False

        return True



    def parse(self,data,current_element):

        if not self.initial_validate(data,current_element):
            return

        clas = self.context + data['@type']

        if "@graph" in data.keys():

            if isinstance(data['@graph'],list):
                for element in data['graph']:
                    self.parse(element,"Element in @graph")

            else:
                self.error += " @graph is not of proper type list."

        for element in data.keys():

            if self.context + element not in self.schema_properties[clas]:
                self.extra_elements.append(element)

            elif isinstance(data[element],dict):
                if self.check_valid_type(data[element],element):
                    self.parse(data[element],element)

            elif isinstance(data[element],list):
                self.validate_list(data[element],element)

            else:
                self.validate_elem(data[element],element)
        return

    def check_valid_type(self,given,prop):

        if "@type" not in given.keys():
            self.error += " " + prop +" is missing required arguement @type."
            return False
        elif self.context + given['@type'] not in self.schema_properties.keys():
            self.error += " " + prop + " not of reconginized class."
            return False

        if self.context + given["@type"] in self.schema_property_ranges[self.context + prop]:
            return True

        elif self.check_super_classes(prop,given['@type']):
            return True

        self.error += " " + str(prop) + " is of incorrect type should be in " \
                    + str(self.schema_property_ranges[self.context + prop])
        return False

    def check_super_classes(self,prop,actual):

        superClasses = [str(f) for f in self.g.transitive_objects(
                rdflib.term.URIRef(actual),
                rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'))]

        for superclass in superClasses:

            if superclass in self.schema_property_ranges[prop]:
                return True

        return False

    def validate_list(self,data,prop):

        for item in data:

            if isinstance(item,dict):
                if self.check_valid_type(item,prop):
                    self.parse(item,prop)

            elif isinstance(item,list):
                self.validate_list(item,prop)

            else:
                self.validate_elem(item,prop)

        return


    def validate_elem(self,item,prop):

        if isinstance(item,(int, float)) and self.context + "Number" not in self.schema_property_ranges[self.context + prop]:
            self.error += " " + prop + " is numeric but should be of type " + str(self.schema_property_ranges[self.context + prop]) + "."
            return

        if not isinstance(item,str):
            self.error += " " + prop + " is of wrong type."

        return


class ShaclValidator(object):

    def __init__(self, data):

        if 'app' in os.listdir():
            f = open("app/schema definitions/shacl definitions.txt", "r")
        else:
            f = open("./schema definitions/shacl definitions.txt", "r")

        self.data = data
        self.shapes_file = f.read()
        self.shapes_file_format = 'turtle'

        self.error = ""
        self.valid = False

    def validate(self):
        if "@context" not in self.data.keys():
            self.data["@context"] = "http://schema.org/"

        testjson = json.dumps(self.data)

        data_file_format = 'json-ld'

        conforms, _, v_text = validate(testjson, shacl_graph=self.shapes_file,
                                        data_graph_format=data_file_format,
                                        shacl_graph_format=self.shapes_file_format,
                                        inference='rdfs', debug=True,
                                        serialize_report_graph=True)

        if conforms:
            self.valid = True
            return

        self.error = v_text
        self.valid = False

        return





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
        if element == "@graph":
            element_seen = True
            if isinstance(testjson[element],list):
                for item in testjson[element]:
                    if isinstance(item,dict):
                        result = validate_json(testjson[element],context,response)
                        error = error + result['error']
                        extra_elements = extra_elements + result['extra_elements']
                    else:
                        error = error + "element in @graph is not of type dictionary, "

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
    testjson["@type"]= testjson["@type"].replace("bio:","")
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
    prop_type = prop_type.replace("bio:","")
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
    if "@context" not in testjson.keys():
        testjson["@context"] = "http://schema.org/"
    testjson = json.dumps(testjson)
    if 'app' in os.listdir():
        f = open("app/schema definitions/shacl definitions.txt", "r")
    else:
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
