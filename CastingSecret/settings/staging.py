from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'casting_secret',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',  # '127.0.0.1'
        'PORT': '5432',  # '5556'
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
MEDIA_ROOT = '/home/ubuntu/casting'

HOST = 'http://54.246.197.87/'

# Elasticsearch configuration
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'elastic:changeme@localhost:9200'
    },
}
