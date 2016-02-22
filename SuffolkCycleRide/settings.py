"""
Django settings for temp project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5l#-+r+1&g2apy^fj7ck14c_-g#8p_jx1llt(-27+n37i^(d$@'

# SECURITY WARNING: don't run with debug turned on in production!


if os.environ.get('PYTHON_ANYWHERE','False') == 'True':
    BASE_URL = 'http://www.suffolkcycleride.org.uk/'
    DEBUG = False
    ALLOWED_HOSTS = ['www.suffolkcycleride.org.uk']
    TEMPLATE_DEBUG = False
else:
    BASE_URL = 'http://192.168.1.78:8000/'
    DEBUG = True
    ALLOWED_HOSTS = []
    TEMPLATE_DEBUG = True

# Application definition

INSTALLED_APPS = [
    'SuffolkCycleRide.apps.SuffolkCycleRideConfig',
    'cyclists.apps.cyclistsConfig',
    'newsletter.apps.newsletterConfig',
    'dashboard.apps.DashboardConfig',
    'stats.apps.StatsConfig',
    'EmailPlus.apps.EmailplusConfig',
    'blog.apps.BlogConfig',
    'Sponsors.apps.SponsorsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'RegisteredUsers.apps.RegisteredUsersConfig',
    'markitup',
    'markdown',
]

# JQUERY_URL = None # Prevent Markitup reloading the JQUERY library
MARKITIUP_AUTO_PREVIEW = True
MARKITUP_FILTER = ('markdown.markdown', {'safe_mode': True})
MARKITUP_SET = 'markitup/sets/markdown/'

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SuffolkCycleRide.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug':TEMPLATE_DEBUG,
            'context_processors': [
                'SuffolkCycleRide.context_processor.settings_base_url',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'SuffolkCycleRide.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

TEST_RUNNER = 'SuffolkCycleRide.tests.testrunner.LayeredTestRunner'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-uk'

TIME_ZONE = 'GMT'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

# Changed to support collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# Defined to collect uploaded Newsletters
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
FILE_UPLOAD_HANDLERS = ['django.core.files.uploadhandler.TemporaryFileUploadHandler']
MEDIA_URL = '/media/'

# Gmail SMTP settings
EMAIL_HOST = 'smtp.mail.yahoo.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = "suffolkcycleride@btinternet.com"
EMAIL_HOST_PASSWORD = "Ball00M0wgl1"
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False

DEFAULT_FROM_EMAIL = "suffolkcycleride@btinternet.com"


#if os.environ.get('PYTHON_ANYWHERE','False') == 'True':
#    EMAIL_VOLUME_LIMIT = 99
#    EMAIL_LIMIT_PERIOD = 24*60*60
#    EMAIL_SCHEDULER_PERIOD = 1200 # Allow a 20 scheduler period - mail will be delayed at least 20 mins.
#else:
#    EMAIL_VOLUME_LIMIT = 99
#    EMAIL_LIMIT_PERIOD = 24*60*60
#    EMAIL_SCHEDULER_PERIOD = 120 # Allow a 2 scheduler period - mail will be delayed at least 2 mins.
