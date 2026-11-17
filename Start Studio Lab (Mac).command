#!/bin/bash
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Studio Lab needs Python 3.9 or newer, and Python was not found."
  echo "Download it from https://www.python.org/downloads/ and run this again."
  read -r -p "Press Enter to close..."
  exit 1
fi
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"; then
  echo "Studio Lab needs Python 3.9 or newer. This Mac has $(python3 --version 2>&1)."
  echo "Download a newer one from https://www.python.org/downloads/ and run this again."
  read -r -p "Press Enter to close..."
  exit 1
fi
python3 -c "import numpy, scipy" 2>/dev/null || python3 -m pip install --user -r requirements.txt
python3 studiolab.py
