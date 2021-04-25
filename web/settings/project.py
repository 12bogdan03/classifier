import environ


env = environ.Env()
environ.Env.read_env()

ENVIRONMENT = env.str('ENVIRONMENT')

if ENVIRONMENT != 'local':
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
