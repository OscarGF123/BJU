import requests
import time
from django.apps import AppConfig
from config import settings
import threading

class AplConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apl'
