import rdflib
import json
import requests
from pyshacl import validate
import pickle
import os

class RDFSValidator(object):

    def __init__(self, data,path = "./static/"):
    # '''
    #     Set up RDFSValidator class, read in json-ld to validate, open RDFS
    #     definition file and parse into ...
    # '''
        self.context = "http://schema.org/"
        self.error = ""
        self.extra_elements = []
        self.data = data

        try:

            #self.g = rdflib.Graph()
            #self.g.parse(path + "g.txt", format="turtle")
            self.superclasses = pickle.load( open(path +  "superclasses.p", "rb" ) )
            self.schema_properties = pickle.load( open(path +  "schema_properties.p", "rb" ) )
            self.schema_property_ranges = pickle.load( open(path +  "schema_property_ranges.p", "rb" ) )

        except:
            with open(path + "schema.jsonld", "rb") as file:
                schema_rdfs = json.loads(file.read())
            with open(path + "rdfs_bioschemas_definition.jsonld","rb") as file:
                bio_rdfs = json.loads(file.read())

            self.g = rdflib.Graph().parse(
                data = json.dumps(bio_rdfs.get("@graph")),
                context=bio_rdfs.get("@context"), format="json-ld",publicID = "http://bioschemas.org/specifications/").parse(
                data = json.dumps(schema_rdfs.get("@graph")),
                context=schema_rdfs.get("@context"), format="json-ld",)
            #self.g = rdflib.Graph().parse(data = json.dumps(schema_rdfs.get("@graph")),
            #context=schema_rdfs.get("@context"), format="json-ld")

            classes = [ elem.get("@id") for elem in schema_rdfs['@graph'] if elem.get("@type") == "rdfs:Class" ]
            properties = [ elem.get("@id") for elem in schema_rdfs['@graph'] if elem.get("@type") == "rdf:Property" ]
            classes.extend([ elem.get("@id") for elem in bio_rdfs['@graph'] if elem.get("@type") == "rdfs:Class" ])
            properties.extend([ elem.get("@id") for elem in bio_rdfs['@graph'] if elem.get("@type") == "rdf:Property" ])

            #self.schema = { elem.get("@id"): elem for elem in schema_rdfs}
            #For now assuming schema is schema.org can exapnd to accept more later



            #Creates list of all properites for each class
            #including those which are inherited from classes above
            self.schema_properties = {}
            self.superclasses = {}
            for clas in classes:
                self.schema_properties[clas] = []

                self.superclasses[clas] = [f for f in self.g.transitive_objects(
                    rdflib.term.URIRef(clas),
                    rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'))]

                for superClass in self.superclasses[clas]:

                    self.schema_properties[clas].extend([str(found)
                        for found in self.g.transitive_subjects(
                                rdflib.term.URIRef("http://schema.org/domainIncludes"),
                                rdflib.term.URIRef(superClass))])

            #Gathers acceptable ranges for all properties found
            self.schema_property_ranges = {}
            for prop in properties:
                self.schema_property_ranges[prop] = [str(f)
                    for f in self.g.transitive_objects(
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
        #data is given jsonld
        #element is where current element in JSON for error reporting

        if not isinstance(data,dict):
            self.error += " " + element + " not of type dict."
            return False

        elif '@type' not in data.keys():
            self.error += " " + element + " missing required property @type."
            return False

        elif not self.recongized_class(data["@type"]):
            self.error += " " + element + " not of reconginized class."
            return False

        return True

    #Determines if given type is recongized by vocab
    def recongized_class(self,given_type):

        given_type = self.update_context(given_type)

        if given_type in self.schema_properties.keys():
            return(True)

        else:
            return(False)

    #Main Validation Function
    #Breaks up json and validates each section
    def parse(self,data,current_element):

        if not self.initial_validate(data,current_element):
            return

        clas = self.update_context(data["@type"])

        if "@graph" in data.keys():

            if isinstance(data['@graph'],list):
                for element in data['graph']:
                    self.parse(element,"Element in @graph")

            else:
                self.error += " @graph is not of proper type list."

        for element in data.keys():

            element_with_context = self.update_context(element)

            if element_with_context not in self.schema_properties[clas]:
                self.extra_elements.append(element)

            elif isinstance(data[element],dict):
                if self.check_valid_type(data[element],element_with_context):
                    self.parse(data[element],element)

            elif isinstance(data[element],list):
                self.validate_list(data[element],element_with_context)

            else:
                self.validate_elem(data[element],element_with_context)
        return

    #Checks to make sure given type (given)
    #is in the allowed classes for the property (prop) it is conntected to
    #   {
    #   'author':{'@type':'Person'}
    #   }
    # {'@type':'Person'} = given
    # 'author' = prop
    def check_valid_type(self,given,prop):

        if "@type" not in given.keys():

            self.error += " " + self.remove_context(prop) + \
                " is missing required arguement @type."

            return False

        given["@type"] = self.update_context(given["@type"])

        if not self.recongized_class(given["@type"]):

            self.error += " " + self.remove_context(prop) +  \
                " not of reconginized class."

            return False

        if given["@type"] in self.schema_property_ranges[prop]:
            return True

        elif self.check_super_classes(prop,given['@type']):
            return True

        self.error += " " + self.remove_context(prop) + \
            " is of incorrect type should be in " \
            + str(self.schema_property_ranges[prop])

        return False

    #similar to check valid classes but looks to see
    #if given class is subclass of acceptable class
    def check_super_classes(self,prop,given_class):

        # superClasses = [str(f) for f in self.g.transitive_objects(
        #         rdflib.term.URIRef(given_class),
        #         rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'))]

        for superclass in self.superclasses[given_class]:

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
        # '''
        #     {
        #     "author":"Justin"
        #     }
        #     here "author" is prop
        #     and "Justin" is the item
        #
        # '''

        if isinstance(item,(int, float)) and self.context + "Number" not in self.schema_property_ranges[prop]:
            self.error += " " + self.remove_context(prop) + " is numeric but should be of type " \
                + str(self.schema_property_ranges[prop]) + "."
            return

        if not isinstance(item,str):
            self.error += " " + self.remove_context(prop) + " is of wrong type."

        return

    #Updates elements to match the way rdflib reads in graphs
    def update_context(self,item):

        if "bio:" in item:
            item = item.replace("bio:","http://bioschemas.org/specifications/")

        elif "http://bioschemas.org/specifications/" in item:
            return(item)

        elif self.context in item:
            return(item)

        else:
            item = self.context + item

        return(item)

    #Removes context for error
    def remove_context(self,prop):

        if isinstance(prop,str):

            return(prop.replace(self.context,"").replace("http://bioschemas.org/specifications/","bio"))

        return(prop)


class ShaclValidator(object):

    def __init__(self, data):

        if 'app' in os.listdir():
            f = open("app/schema definitions/shacl definitions.txt", "r")
        else:
            f = open("./schema definitions/Dataset shacl.ttl", "r")

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
