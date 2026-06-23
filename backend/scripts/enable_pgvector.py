#!/usr/bin/env python
"""Enable pgvector extension on PostgreSQL."""
import os
import sys
from pathlib import Path

import django

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    print("pgvector extension enabled.")
