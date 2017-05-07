"""
Server config
"""


## for Docker on domino.cs.rit.edu, use:
## first verify external IP with
# $ ip addr
## then verify Docker's exposed IP with same command but within Docker container
## expecting: 172.17.0.2
## finally, run:
# $ docker run -p 129.21.37.42:1070:1070 -it mey5634/diffsync:diffsynch_proj
## then verify that domino.cs.rit.edu opened the IPv4 port:
# $ netstat -nap | grep 1070
## expected output:
## tcp        0      0 129.21.37.42:1070       0.0.0.0:*               LISTEN      -


DEBUG = True

HOST = {
        'DEV': '127.0.0.1',
        'PROD': '172.17.0.6'
       }

PORT = {
        'DEV': 8080,
        'PROD': 1070
       }

