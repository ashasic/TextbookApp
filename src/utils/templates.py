import os
from fastapi.templating import Jinja2Templates

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # -> TextbookApp
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

print("TEMPLATES_DIR:", TEMPLATES_DIR)  # 🧪 Add this line temporarily

templates = Jinja2Templates(directory=TEMPLATES_DIR)
