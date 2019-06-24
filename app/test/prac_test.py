import unittest
import requests
from app import app

class Testflaskapp(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()
    def test_valid_json(self):
        testjson = {'@context': "http://json-schema.org/draft-07/schema","@type":"Dataset","name":"Justin"}
        URL = " http://127.0.0.1:5000/validatejson"
        r = requests.post(url = URL,json = testjson)
        self.assertEqual(r.json(), {'valid':True,'non schema properties':[]})
    
    def test_extra_property(self):
        testjson = {'@context': "http://json-schema.org/draft-07/schema","@type":"Dataset","name":"Justin","randomname":"test"}
        URL = " http://127.0.0.1:5000/validatejson"
        r = requests.post(url = URL,json = testjson)
        self.assertEqual(r.json(), {'valid':True,'non schema properties':["randomname"]})
if __name__ == '__main__':
    unittest.main()