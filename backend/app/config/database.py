import os
from databases import Database
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Build the connection string
DATABASE_URL = f"mysql+aiomysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

# Create the database instance
database = Database(DATABASE_URL)