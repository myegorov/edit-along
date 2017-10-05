#!/bin/bash

docker rm $(docker ps -qa)
docker rmi -f $(docker images -qa -f 'dangling=true')

# build container
NAME="edit-along"
docker build --no-cache=true -t $NAME .

# run container
docker run -p 1070:1070 $NAME:latest
