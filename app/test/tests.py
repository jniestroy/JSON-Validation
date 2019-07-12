import unittest
import requests
import app
import validate
#import sys
#sys.path.append(".")

class test_initial_validate(unittest.TestCase):
    def test_check_working_initial(self):
        val = validate.RDFSValidator({"@type":"Dataset"})
        check = val.initial_validate({"@type":"Dataset"},"test")
        self.assertEqual(check,True)
    def test_failing_initial(self):
        val = validate.RDFSValidator({"@type":"Datase1212"})
        check = val.initial_validate({"@type":"Datas1212"},"test")
        self.assertEqual(check,False)
class test_check_valid_type(unittest.TestCase):
    def test_invalid_type(self):
        val = validate.RDFSValidator({"@type":"Dataset"})
        check = val.check_valid_type({"@type":"Animal"},"author")
        self.assertEqual(check,False)

class Testflaskapp(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()
    def test_valid_json(self):
        testjson = {
  "@context":{ "@vocab": "http://schema.org/" },
  "@type":"Dataset",
  "name":"sample",
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
        r = self.app.post('/validatejson',json = testjson)
        self.assertEqual(r.json, {'error': '', 'extra_elements': [], 'valid': True})

    def test_extra_property(self):
        testjson = {
  "@context":{ "@vocab": "http://schema.org/" },
  "@type":"Dataset",
  "randomname":"this should fail",
  "name":"sample",
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
        r = self.app.post('/validatejson',json = testjson)
        self.assertEqual(r.json, {'error': '', 'extra_elements': ["randomname"], 'valid': True})
    def test_no_json(self):
        r = self.app.post('/validatejson')
        self.assertEqual(r.json, {'error':"Please POST JSON file",'valid':False})
if __name__ == '__main__':
    unittest.main()
