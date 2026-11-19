"""
Configurações do projeto Padaria Doce & Ponto.
Banco de dados: PostgreSQL hospedado no Neon (https://neon.tech).
"""

from pathlib import Path

from decouple import config
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = config("DEBUG", default=True, cast=bool)
SECRET_KEY = config("SECRET_KEY", default="")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("Defina SECRET_KEY no ambiente antes de iniciar em produção.")
    SECRET_KEY = "django-insecure-chave-apenas-para-desenvolvimento"
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_filters",
    "confeitaria",
    "ia",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# App Engine terminates HTTPS at its frontend and forwards this trusted header.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ROOT_URLCONF = "nucleo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "base_layout",
            BASE_DIR / "apps" / "ia" / "templates",
            BASE_DIR / "confeitaria" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "confeitaria.context_processors.grupos_do_usuario",
            ],
        },
    },
]

WSGI_APPLICATION = "nucleo.wsgi.application"

# A pasta de migrações deste app se chama "migracoes" (em português) em vez
# do padrão "migrations" do Django — por isso o mapeamento abaixo é necessário.
MIGRATION_MODULES = {
    "confeitaria": "confeitaria.migracoes",
}

# ---------------------------------------------------------------------------
# Banco de dados — Neon (PostgreSQL serverless)
# Defina a string de conexão nas variáveis de ambiente abaixo (veja .env.exemplo)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("PGDATABASE", default="padaria"),
        "USER": config("PGUSER", default=""),
        "PASSWORD": config("PGPASSWORD", default=""),
        "HOST": config("PGHOST", default=""),
        "PORT": config("PGPORT", default="5432"),
        "OPTIONS": {"sslmode": "require"},
    }
}

# Apenas para a suíte local, sem substituir o PostgreSQL de desenvolvimento ou produção.
if config("USE_SQLITE", default=False, cast=bool):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default=(
        "django.core.mail.backends.console.EmailBackend"
        if DEBUG
        else "django.core.mail.backends.smtp.EmailBackend"
    ),
)
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="Padaria Doce & Ponto <webmaster@localhost>")

# Assistente: sem chave, a resposta usa o cardápio local. A URL deve ser um endpoint
# compatível com chat completions e a chave fica só no ambiente.
IA_API_URL = config("IA_API_URL", default="")
IA_API_KEY = config("IA_API_KEY", default="")
IA_MODELO = config("IA_MODELO", default="")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Autenticação: para onde redirecionar quem não está logado (LoginRequiredMixin)
# e para onde ir após entrar/sair.
# ---------------------------------------------------------------------------
LOGIN_URL = "confeitaria:entrar"
LOGIN_REDIRECT_URL = "confeitaria:produto_lista"
LOGOUT_REDIRECT_URL = "confeitaria:entrar"
