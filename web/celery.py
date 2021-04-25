from __future__ import absolute_import, unicode_literals

import os
import sys


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')

current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(current_path, "apps"))

