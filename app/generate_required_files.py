import rdflib
import json
import pickle
path = "./static/"
with open(path + "schema.jsonld", "rb") as file:
    schema_rdfs = json.loads(file.read())
with open(path + "rdfs_bioschemas_definition.jsonld","rb") as file:
    bio_rdfs = json.loads(file.read())

g = rdflib.Graph().parse(
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
schema_properties = {}
for clas in classes:
    schema_properties[clas] = []

    superClasses = [f for f in g.transitive_objects(
        rdflib.term.URIRef(clas),
        rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'))]

    for superClass in superClasses:

        schema_properties[clas].extend([str(found)
            for found in g.transitive_subjects(
                    rdflib.term.URIRef("http://schema.org/domainIncludes"),
                    rdflib.term.URIRef(superClass))])

#Gathers acceptable ranges for all properties found
schema_property_ranges = {}
for prop in properties:
    schema_property_ranges[prop] = [str(f)
        for f in g.transitive_objects(
                rdflib.term.URIRef(prop),
                rdflib.term.URIRef("http://schema.org/rangeIncludes"))]

pickle.dump(schema_properties, open(path + "schema_properties.p", "wb" ) )
g.serialize(destination=path + 'g.txt', format='turtle')
pickle.dump(schema_property_ranges, open( path + "schema_property_ranges.p", "wb" ) )
