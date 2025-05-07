import os
from fastapi.templating import Jinja2Templates

# BASE_DIR should go up only ONE level from src/utils → src → TextbookApp
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # => TextbookApp
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

print("✅ TEMPLATES_DIR:", TEMPLATES_DIR)  # Optional debug print

templates = Jinja2Templates(directory=TEMPLATES_DIR)
