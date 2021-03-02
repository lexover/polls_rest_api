# REST API for conducting polls.

It's implementation of REST API for conducting polls using Django REST Framework. The pytest is used for testing, Swagger wiht drf-yasg used for documenting API, Postgres is used as database. 
To run this app you should have installed [Docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/). 

To build Docker images and run it clone this repo, and inside it run docker-compose up:
```sh
clone https://github.com/lexover/polls_rest_api.git
cd polls_rest_api
docker-compose up --build -d
```
To stop Docker images run:
```sh
docker-compose down -v
```

When it started API available by: http://localhost:8000, documentation available by: http://localhost:8000/swagger/.

A production build is also available. Production build is also available. It uses Gunicorn as an application server and nginx as a reverse proxy. To start it run:
```sh
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear
```

After start API will be available by address: http://localhost:1337/, documentation by: http://localhost:1337/swagger/
