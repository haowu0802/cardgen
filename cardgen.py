"""
A stateless web app for generating cards
"""
import os  # for env var
import sys  # for using manage.py with arguments
from django.conf import settings  # for Django settings, settings must be set before importing other components

# env dependent settings
DEBUG = os.environ.get('DEBUG', 'on') == 'on'  # get debug flag from env, default on
SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))  # get secret_key from env, default 32 b rand
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')  # allowing all

# the settings, typically in settings.py
settings.configure(
    DEBUG=DEBUG,  # using debug mode
    SECRET_KEY=SECRET_KEY,  # env dependent
    ALLOWED_HOSTS=ALLOWED_HOSTS,  # env dep
    ROOT_URLCONF=__name__,  # point outing to the right place
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ),
)


"""above this point needs to run before below"""
from django import forms  # for validation of attack and defence
from PIL import Image  # image processor
from io import BytesIO  # byte manipulator
from django.conf.urls import url  # for routing in controller
from django.http import HttpResponse, HttpResponseBadRequest  # for constructing response in views
from django.core.wsgi import get_wsgi_application  # wsgi application for prod server, usually in wsgi.py

application = get_wsgi_application()  # init wsgi app


class CardForm(forms.Form):
    """used as a validator for input attack and defence values"""
    height = forms.IntegerField(min_value=1, max_value=1024)
    width = forms.IntegerField(min_value=1, max_value=1024)

    def generate(self, image_format='PNG'):  # default format png
        """generate the card image, return raw bytes"""
        height = self.cleaned_data['height']
        width = self.cleaned_data['width']
        image = Image.new('RGB', (width, height))  # pillow takes color, (w,h)
        content = BytesIO()  # init content to be transferred as raw bytes
        image.save(content, image_format)  # save image to content buffer with format
        content.seek(0)  # rewind content to beginning
        return content  # content is raw bytes


def cardgen(request, height, width):
    """attack defence, as 2 params for the generator"""
    # init form obj for validation
    form = CardForm({
        'height': height,
        'width': width,
    })
    if form.is_valid():
        image = form.generate()  # generate image and ready to send
        return HttpResponse(image, content_type='image/png')  # send image
    else:
        return HttpResponseBadRequest('Invalid Card Request')  # send 400 when value not valid


def index(request):
    """the view, typically in a view.py file, but that's not a requirement of Django"""
    return HttpResponse('Card Generator')


"""the routing, typically in a urls.py file"""
urlpatterns = (
    # 15x10 => height=15 x width=10 => card/320x200/
    url(r'^card/(?P<height>[0-9]+)x(?P<width>[0-9]+)/$', cardgen, name='cardgen'),
    url(r'^$', index, name='homepage'),  # naming route for templates
)


if __name__ == "__main__":
    """ import the execution method to enable manage cmd"""
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

