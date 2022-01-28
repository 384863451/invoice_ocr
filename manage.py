#!/usr/bin/env python
import os
import sys
import matplotlib
import seaborn
import utils.autoanchor
import utils
import utils.torch_utils
import util.qrcode
import tqdm
import matplotlib
import models.yolo

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "invoice_ocr.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
