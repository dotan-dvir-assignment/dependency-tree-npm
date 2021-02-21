import requests
import time
import unittest


# Runs a few simple tests. Please ensure the main server is running and listening on port 5000.

class TestDependencyPrinter(unittest.TestCase):
    def testShortDependency(self):
        response = requests.get("http://localhost:5000/loadsh")

        assert(response.status_code==200)

    def testWrongDependency(self):
        response = requests.get("http://localhost:5000/xyz3939w")

        assert(response.status_code==400)

    def testLongDependency(self):
        response = requests.get("http://localhost:5000/express")

        assert (response.status_code == 200)

    def testCaching(self):
        first_start = time.time()
        response = requests.get("http://localhost:5000/hapi")
        first_end = time.time()

        assert(response.status_code == 200)

        second_start = time.time()
        response = requests.get("http://localhost:5000/hapi")
        second_end = time.time()

        assert(response.status_code == 200)
        assert(first_end-first_start>second_end-second_start)


if __name__ == '__main__':
    unittest.main()