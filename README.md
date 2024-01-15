# django-api

Recepies API built with Python and Django

## Application use

The app is running inside the Docker container, so to be able to use the app you need the Docker to be installed in your system.

To start the server use:
`docker-compose up`

To stop the server use:
`Control + C` keys

To remove container from the Docker use:
`docker-compose down`

## Tests

To run tests use this command:
`docker-compose run --rm app sh -c "python manage.py test"`
