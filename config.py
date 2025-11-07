# config.py
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Flask server settings
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', 5000))

# Tableau settings using PAT
TABLEAU_SERVER = os.getenv('TABLEAU_SERVER')
TABLEAU_SITE_ID = os.getenv('TABLEAU_SITE_ID', '')
TABLEAU_PAT_NAME = os.getenv('TABLEAU_PAT_NAME')
TABLEAU_PAT_SECRET = os.getenv('TABLEAU_PAT_SECRET')
TABLEAU_PROJECT_NAME = os.getenv('TABLEAU_PROJECT_NAME', 'Sales')
