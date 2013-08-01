from local_settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['bangatuchicago.com']

STATIC_ROOT = os.path.join(SITE_ROOT, 'static')

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
		'LOCATION': '127.0.0.1:11211',
	}
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

BROKER_URL = "amqp://guest@localhost/"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
