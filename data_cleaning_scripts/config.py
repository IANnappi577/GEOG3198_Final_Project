import os
from dotenv import load_dotenv

# keeping this here in case I use a .env in the future
# load_dotenv()

# Our goal projection for the project to keep it in one place
PROJECTION = os.getenv('PROJECTION', 'EPSG:26985')