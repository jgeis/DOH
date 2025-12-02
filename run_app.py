#!/usr/bin/env python
"""
Wrapper script to run multi_dashboard.py with Jupyter mode disabled
"""
import os
import sys

# Disable Jupyter/IPython detection before importing dash
os.environ['DASH_JUPYTER_MODE'] = 'off'

# Also prevent IPython from being detected
if 'IPython' in sys.modules:
    del sys.modules['IPython']

# Now run the dashboard
import multi_dashboard
