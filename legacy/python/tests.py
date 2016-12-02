__author__ = 'scottsfarley'
import requests

import unittest

baseURL = "http://localhost:8000/"

class TestGETVariablesEndpoint(unittest.TestCase):
    def testResponseCode(self):
        url = baseURL + "variables"
        request = requests.get(url)
        self.assertEqual(request.status_code, 200)

class TestPOSTVariablesEndpoint(unittest.TestCase):
    def testWithoutReqVars(self):
        ## without required variables should return status 400
        url = baseURL + "variables"
        request = requests.post(url)
        self.assertEqual(request.status_code, 400)

    def testWithReqVars(self):
        ## with required variables should return status 201
        url = baseURL + "variables"
        data = {
            "variableType": "Tmax",
            "variablePeriod" :  2,
            "variablePeriodType" : "Month",
            "averagingPeriod" : 1,
            "aveagingPeriodType" : "Decade",
            "variableUnits" : "F"
        }
        request = requests.post(url, data=data)
        self.assertEqual(request.status_code, 201)
    def testDuplicate(self):
        ## with required variables, duplicates, should return status 200
        url = baseURL + "variables"
        data = {
            "variableType": "Tmax",
            "variablePeriod" :  2,
            "variablePeriodType" : "Month",
            "averagingPeriod" : 1,
            "aveagingPeriodType" : "Decade",
            "variableUnits" : "F"
        }
        request = requests.post(url, data=data)
        self.assertEqual(request.status_code, 200)




if __name__ == '__main__':
    unittest.main()