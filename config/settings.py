# Basic settings
import os
from envparse import env

UPWORK_STATUS = 'https://api.status.io/1.0/status/55a1f951d0ef560d6e00006e'

BOT_TOKEN = env('BOT_TOKEN')
# admins chat_id list
ADMINS = env('ADMINS', cast=list, default=(''))
# logging mode
DEBUG = env('DEBUG', cast=bool, default=False)
MIN_UPDATE_PERIOD = env('MIN_UPDATE_PERIOD', cast=int, default=100)
MAX_FEED_COUNT = env('MAX_FEED_COUNT', cast=int, default=3)

#db settings
DB_HOST = env('DB_HOST', default='mongo')
DB_PORT = env('DB_PORT', cast=int, default=27017)
DB_NAME = env('DB_NAME', default='uplance')
DB_MAX_POOL_SIZE = env('DB_MAX_POOL_SIZE', cast=int, default=300)
