import os
from databases import Database
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Safely grab the variables (defaulting port to 4000 for TiDB)
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT', '4000')

# Build the connection string WITH the port and SSL required by TiDB
DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?ssl=true"

# Create the database instance
database = Database(DATABASE_URL)