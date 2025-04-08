"""
Django settings for api_ecommerce project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
from dotenv import load_dotenv, find_dotenv
import os
from pathlib import Path
import pymysql
pymysql.install_as_MySQLdb()  # Makes PyMySQL mimic mysqlclient

load_dotenv(find_dotenv())

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = r'django-insecure-o#pdi%udpf=0g9n2wupct7yw#*!467rxjv(t1wenh3d$@e^%oa'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'api_ecommerce.api.apps.ApiConfig',  # API app
    'drf_yasg',  # Swagger
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'api_ecommerce.api.middleware.CustomAllowedHostsMiddleware'
]
CORS_ALLOW_ALL_ORIGINS = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'api_ecommerce.api_ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'api_ecommerce.wsgi.application'

CORS_ALLOWED_ORIGINS = [
    "https://projeto-ibmec-cloud-9016-2025-f8hhfgetc3g3a2fg.centralus-01.azurewebsites.net",
    "http://localhost:8000",
]

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("SQL_DATABASE"),  # Replace with your database name
        'USER': os.getenv("SQL_USERNAME"),  # Replace with your database user
        'PASSWORD': os.getenv("SQL_PASSWORD"),  # Replace with your database password
        'HOST': os.getenv("SQL_SERVER"),  # Replace with your database host
        'PORT': os.getenv("SQL_PORT"),  # Replace with your database port
        'OPTIONS': {
            'ssl': {
                'ca': os.path.join(BASE_DIR, 'DigiCertGlobalRootCA.crt.pem'),
                'ssl_mode': 'REQUIRED'  # Force SSL
            },
            'charset': 'utf8mb4',
        }

    }
}
COSMOS_DB = {
    "URI": os.getenv("COSMOS_URI"),  # Replace with your Cosmos DB URI
    "KEY": os.getenv("COSMOS_PRIMARY_KEY"),  # Replace with your Cosmos DB key
    "DATABASE_NAME": os.getenv("COSMOS_DB_NAME"),  # Replace with your database name
    "COLLECTIONS": {
        "PRODUTOS": "produtos",  # Collection para produtos
        "PEDIDOS": "pedidos",  # Collection para pedidos
    },
    "QUERY_METRICS_ENABLED": True,  # Optional: Enable query metrics
    "RESPONSE_DIAGNOSTICS_ENABLED": True,  # Optional: Enable response diagnostics
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MIGRATION_MODULES = {
    # Desabilita criação de tabelas default na DB relacional.
    'api': None,        
}

#migration