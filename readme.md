A light-weighted implementation of a Django image generator server
---
It's a simple image generating server that generates and caches images requested of a certain width and height, that are best used as placeholders.


This server is based on the light-weight Django template

https://github.com/haowu0802/single_file_django_hello/tree/single-file-django-template

A working instance of this web service can be found here:

https://cardgen.herokuapp.com/

p.s. It will take a few seconds to load when it's visited after a long period of idle. Heroku host goes into hiberanation when not visited.


To run:
---
  dev:      python cardgen.py runserver
  
  staging:  gunicorn cardgen
  
  prod:     gunicorn cardgen
  


Dependencies:
---
  Django==1.11.3
  
  gunicorn==19.7.1
  
  whitenoise==3.2
  
  pillow==4.2.1