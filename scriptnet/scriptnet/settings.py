"""
Django settings for scriptnet project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
from django.contrib.messages import constants as message_constants
# Message tags
MESSAGE_TAGS = {
    message_constants.ERROR: 'danger',
}


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'h-#dw753y3coq1qby791q5#@x*5orij&avx1!rib@ogb$valb6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'competitions.apps.CompetitionsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'django_tables2'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'scriptnet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',                
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
				"competitions.context_processors.language_form_context_processor",
            ],
        },
    },
]

WSGI_APPLICATION = 'scriptnet.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


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

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

LANGUAGE_CODE = 'en'
from django.utils.translation import ugettext_lazy as _
LANGUAGES = [
	('bg', _('Bulgarian')),
	('hr', _('Croatian')),
	('cs', _('Czech')),
	('da', _('Danish')),
	('nl', _('Dutch')),
	('en', _('English')),
	('et', _('Estonian')),
	('fi', _('Finnish')),
	('fr', _('French')),
	('de', _('German')),
	('el', _('Greek')),
	('hu', _('Hungarian')),
	('ga', _('Irish')),
	('it', _('Italian')),
	('lv', _('Latvian')),
	('lt', _('Lithuanian')),
	('pl', _('Polish')),
	('pt', _('Portuguese')),
	('ro', _('Romanian')),
	('sk', _('Slovak')),
	('sl', _('Slovenian')),
	('es', _('Spanish')),
	('sv', _('Swedish')),

];

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

# Media -- Uploaded files from users. This may or may not include public & private training & test sets

MEDIA_URL = '/media/'


