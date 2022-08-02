

import os
import shutil
from pathlib import Path
from django.test import TestCase, override_settings
from django.conf import settings


TEST_MEDIA_ROOT: Path = settings.BASE_DIR/ 'test-media/'

print('Test Media Root', TEST_MEDIA_ROOT)

@override_settings(STATICFILES_STORAGE='whitenoise.storage.CompressedStaticFilesStorage')
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CustomTestClass(TestCase):
    def setUp(self):
        if not TEST_MEDIA_ROOT.exists():
            os.makedirs(TEST_MEDIA_ROOT)
        super().setUp()
        
    def tearDown(self):
        if  TEST_MEDIA_ROOT.exists():
            shutil.rmtree(TEST_MEDIA_ROOT)
        super().tearDown()