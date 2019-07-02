import unittest
import requests
from app import app

class Testflaskapp(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()
    def test_valid_json(self):
        testjson = {'@context': "http://json-schema.org/draft-07/schema","@type":"Dataset","name":"Justin","description":"Test dataset","dataCreated":"5/12/1990",author:{"name":"check",url:"test"}}
        URL = " http://127.0.0.1:5000/validatejson"
        r = self.app.post('/validatejson',json = testjson)
        self.assertEqual(r.json, {'error': '', 'extra_elements': [], 'valid': True})
    
    def test_extra_property(self):
        testjson = {'@context': "http://json-schema.org/draft-07/schema","@type":"Dataset","name":"Justin","description":"Test dataset","dataCreated":"5/12/1990",author:{"name":"check",url:"test"},"random":"test"}
        URL = " http://127.0.0.1:5000/validatejson"
        r = self.app.post('/validatejson',json = testjson)
        self.assertEqual(r.json, {'error': '', 'extra_elements': ["randomname"], 'valid': True})
    def test_missing_property(self):
        testjson = testjson = {
  "@context":{ "@vocab": "http://schema.org/" },
  "@type":"Dataset",
  "dateCreated":"19/9/1995",
  "description":"Storm Data is provided by the National Weather Service (NWS) and contain statistics on...",
  "url":"https://catalog.data.gov/dataset/ncdc-storm-events-database",
  "sameAs":"https://gis.ncdc.noaa.gov/geoportal/catalog/search/resource/details.page?id=gov.noaa.ncdc:C00510",
  "identifier": ["https://doi.org/10.1000/182",
                 "https://identifiers.org/ark:/12345/fk1234"],
  "keywords":[
     "ATMOSPHERE > ATMOSPHERIC PHENOMENA > CYCLONES",
     "ATMOSPHERE > ATMOSPHERIC PHENOMENA > DROUGHT",
     "ATMOSPHERE > ATMOSPHERIC PHENOMENA > FOG",
     "ATMOSPHERE > ATMOSPHERIC PHENOMENA > FREEZE"
  ],
  "author":{
     "@type":"Organization",
     "url": "https://www.ncei.noaa.gov/",
     "name":"OC/NOAA/NESDIS/NCEI > National Centers for Environmental Information, NESDIS, NOAA, U.S. Department of Commerce",
     "contactPoint":{
        "@type":"ContactPoint",
        "contactType": "customer service",
        "telephone":"+1-828-271-4800",
        "email":"ncei.orders@noaa.gov"
     }
  },
  "includedInDataCatalog":{
     "@type":"DataCatalog",
     "name":"data.gov"
  },
  "distribution":[
     {
        "@type":"DataDownload",
        "encodingFormat":"CSV",
        "contentUrl":"http://www.ncdc.noaa.gov/stormevents/ftp.jsp"
     },
     {
        "@type":"DataDownload",
        "encodingFormat":"XML",
        "contentUrl":"http://gis.ncdc.noaa.gov/all-records/catalog/search/resource/details.page?id=gov.noaa.ncdc:C00510"
     }
  ]
}
        URL = " http://127.0.0.1:5000/validatejson"
        r = self.app.post('/validatejson',json = testjson)
        self.assertEqual(r.json,{'error': 'Validation Report\nConforms: False\nResults (1):\nConstraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):\n\tSeverity: sh:Violation\n\tSource Shape: [ sh:datatype xsd:string ; sh:minCount Literal("1", datatype=xsd:integer) ; sh:name Literal("dataset name") ; sh:path schema:name ]\n\tFocus Node: [ ]\n\tResult Path: schema:name\n', 'extra_elements': [], 'valid': False})
    def test_no_json(self):
        testjson = 'randomstring'
        URL = " http://127.0.0.1:5000/validatejson"
        r = self.app.post('/validatejson')
        self.assertEqual(r.json, {'error':"Please POST JSON file",'valid':False})
if __name__ == '__main__':
    unittest.main()