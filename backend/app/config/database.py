import os
from databases import Database
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Safely grab the variables (defaulting to local settings if .env is missing)
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'placement_management')
DB_PORT = os.getenv('DB_PORT', '3306')

# Build the base connection string
DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SMART CHECK: Only add SSL if we are connecting to TiDB Cloud!
if "tidbcloud" in DB_HOST:
    DATABASE_URL += "?ssl=true"

# Create the database instance
database = Database(DATABASE_URL)