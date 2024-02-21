import os.path

import fastapi.templating

template_dir = os.path.join(os.path.dirname(__file__), "static")

template = fastapi.templating.Jinja2Templates(template_dir)
