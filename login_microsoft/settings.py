from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ia!$x61@^@15kr)2)oq2zt1)98ja3&9fiu_gcdi0i1g^%@7k+z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'tela_login_microsoft',
    'TI',
    'RH',
    'FINANCEIRO',
    'CONTABILIDADE',
    'MARKETING',
    'LOGISTICA',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'login_microsoft.urls'

AUTHENTICATION_BACKENDS = [
    'social_core.backends.azuread_tenant.AzureADTenantOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY = '0c1c7c9c-c1f7-431c-a238-1b53a950a9d6'
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET = 'o6I8Q~XysOcUWg1WZlSzAv9iAzep0SJfmLaHzc3Q'
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID = 'familiadositio.com.br' 

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',  
                'social_django.context_processors.login_redirect', 
            ],
        },
    },
]

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'tela_login_microsoft.pipeline.redirect_by_department', 
)

WSGI_APPLICATION = 'login_microsoft.wsgi.application'


SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_REDIRECT_URI = 'http://localhost:8000/oauth/complete/azuread-tenant-oauth2/'

SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_EXTRA_DATA = ['department']
SECURE_SSL_REDIRECT = False

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

LOGIN_URL = 'login'              # Onde está o botão de login
LOGOUT_URL = 'logout'            # Rota que limpa a sessão
LOGIN_REDIRECT_URL = 'base' # Rota para onde o usuário é redirecionado após o login
