"""
A stateless web app for generating cards
"""
import os  # for env var
import sys  # for using manage.py with arguments
import hashlib  # for generating hash for client cache

from PIL import Image, ImageDraw  # image processor, and drawer
from io import BytesIO  # byte manipulator

from django.conf import settings  # for Django settings, settings must be set before importing other components

# env dependent settings
DEBUG = os.environ.get('DEBUG', 'on') == 'on'  # get debug flag from env, default on
SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))  # get secret_key from env, default 32 b rand
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')  # allowing all
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # base dir of app

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
    INSTALLED_APPS=(
        'django.contrib.staticfiles',
    ),
    TEMPLATES=(
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                # insert your TEMPLATE_DIRS here
                os.path.join(BASE_DIR, 'templates'),
            ],
            'APP_DIRS': True,
        },
    ),
    STATICFILES_DIRS=(
        os.path.join(BASE_DIR, 'static'),
    ),
    STATIC_ROOT=os.path.join(BASE_DIR, 'staticfiles'),
    STATIC_URL='/static/',
    STATICFILES_STORAGE='whitenoise.django.GzipManifestStaticFilesStorage',
)


"""above this point needs to run before below"""
from django import forms  # for validation of attack and defence

from django.core.cache import cache  # core server cache
from django.views.decorators.http import etag  # client cache

from django.core.urlresolvers import reverse  # for reversing a url for home view example
from django.shortcuts import render  # for rendering views

from django.conf.urls import url  # for routing in controller
from django.http import HttpResponse, HttpResponseBadRequest  # for constructing response in views

from django.core.wsgi import get_wsgi_application  # wsgi application for prod server, usually in wsgi.py
from whitenoise.django import DjangoWhiteNoise  # for serving static files in Heroku

application = get_wsgi_application()  # init wsgi app
application = DjangoWhiteNoise(application)  # add whitenoise static file support


class CardForm(forms.Form):
    """used as a validator for input attack and defence values"""
    height = forms.IntegerField(min_value=1, max_value=1024)
    width = forms.IntegerField(min_value=1, max_value=1024)

    def generate(self, image_format='PNG'):  # default format png
        """generate the card image, return raw bytes"""
        height = self.cleaned_data['height']
        width = self.cleaned_data['width']

        """cache"""
        key = '{}.{}.{}'.format(width, height, image_format)
        content = cache.get(key)  # read from cache

        if content is None:  # no cached data found
            image = Image.new('RGB', (width, height))  # pillow takes color, (w,h)

            # make drawings on the card
            draw = ImageDraw.Draw(image)  # set drawer on image
            text = '{} X {} '.format(height, width)  # prepare text and format
            textwidth, textheight = draw.textsize(text)  # get text size from prepared text
            if textwidth < width and textheight < height:  # make sure text is within card
                texttop = (height - textheight) // 2  # top pix of text
                textleft = (width - textwidth) // 2  # left pix of text
                draw.text(
                    (textleft, texttop),  # top left pos
                    text,  # text content
                    fill=(255, 255, 255),  # color of text
                )

            content = BytesIO()  # init content to be transferred as raw bytes
            image.save(content, image_format)  # save image to content buffer with format
            content.seek(0)  # rewind content to beginning
            cache.set(key, content, 60*60)  # cached for 1H

        return content  # content is raw bytes


def generate_etag(request, width, height):
    """generate etag for browser cache"""
    content = 'Card:{0}x{1}'.format(width, height)
    return hashlib.sha1(content.encode('utf-8')).hexdigest()


@etag(generate_etag)  # decorate view with generated etag for browser cache
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
    """a home page for showing some examples"""
    example = reverse('cardgen', kwargs={'width': 50, 'height': 50})
    context = {
        'example': request.build_absolute_uri(example)
    }
    return render(request, 'home.html', context)


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

