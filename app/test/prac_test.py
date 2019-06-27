import unittest
import requests
from app import app

class Testflaskapp(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()
    def test_valid_json(self):
        testjson = {'@context': "http://json-schema.org/draft-07/schema","@type":"Dataset","name":"Justin"}
        URL = " http://127.0.0.1:5000/validatejson"
        r = self.app.post('/validatejson',json = testjson)
        self.assertEqual(r.json, {'valid':True,'non schema properties':[]})
    
    def test_extra_property(self):
        testjson = {'@context': "http://json-schema.org/draft-07/schema","@type":"Dataset","name":"Justin","randomname":"test"}
        URL = " http://127.0.0.1:5000/validatejson"
        r = self.app.post('/validatejson',json = testjson)
        self.assertEqual(r.json, {'valid':True,'non schema properties':["randomname"]})
    def test_no_json(self):
        testjson = 'randomstring'
        URL = " http://127.0.0.1:5000/validatejson"
        r = self.app.post('/validatejson')
        self.assertEqual(r.json, {'error':"Please POST JSON file",'valid':False})
if __name__ == '__main__':
    unittest.main()