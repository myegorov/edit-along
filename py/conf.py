"""
Server config
"""

DEBUG = True

HOST = {
        'DEV': '127.0.0.1',
        'PROD': '172.17.0.6' # ip exposed by Docker
       }

PORT = {
        'DEV': 8080,
        'PROD': 1070
       }

