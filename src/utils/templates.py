# src/utils/templates.py
from fastapi.templating import Jinja2Templates

# point at your templates directory just once
templates = Jinja2Templates(directory="templates")
