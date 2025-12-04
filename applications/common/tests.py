from django.test import TestCase
from applications.common.tasks import debug_task

# Create your tests here.

debug_task.delay()