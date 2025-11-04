import os
from dotenv import load_dotenv

# Get the absolute path of the directory where this file is located
basedir = os.path.abspath(os.path.dirname(__file__))
# Load environment variables from a .env file (for SECRET_KEY)
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """
    Set Flask configuration vars from .env file or defaults.
    """
    
    # --- General Config ---
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-hard-to-guess-string'
    
    # --- Database Config ---
    # We point this to the 'instance' folder, which is a safer
    # place to store database files, separate from your main code.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'smart_recycler.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- NEW UPLOAD CONFIG ---
    # Define the upload folder inside the 'instance' folder
    # This is where your donation images will be saved.
    UPLOAD_FOLDER = os.path.join(basedir, 'instance', 'uploads')