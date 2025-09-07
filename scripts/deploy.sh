#!/bin/sh

git restore .
git pull origin main

docker build . -t scholarx-backend

docker-compose down
docker-compose up -d
