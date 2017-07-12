A light-weighted implementation of a Django image generator server

This server is based on the light-weight Django template https://github.com/haowu0802/single_file_django_hello/tree/single-file-django-template

It's a simple image generating server that generates and caches images requested of a certain width and height, that are best used as placeholders.
 
To run:
  dev:      python cardgen.py runserver
  staging:  gunicorn cardgen --log-files=-
  prod:     gunicorn cardgen --log-files=-