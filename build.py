import os
import shutil
import re
from jinja2 import Environment, FileSystemLoader

# Define directories
BUILD_DIR     = 'build'
STATIC_DIR    = 'static'
TEMPLATES_DIR = 'templates'

def create_build_dir():
    """Create clean build directory, with a static subfolder."""
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(os.path.join(BUILD_DIR, 'static'), exist_ok=True)

def copy_static_files():
    """Copy all static subfolders into build/static/..."""
    for sub in ['css', 'js', 'assets', 'uploads']:
        src = os.path.join(STATIC_DIR, sub)
        dst = os.path.join(BUILD_DIR, 'static', sub)
        if os.path.exists(src):
            shutil.copytree(src, dst)

def render_templates():
    """Render all Jinja templates to static HTML in build/."""
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    for fname in os.listdir(TEMPLATES_DIR):
        if fname.endswith('.html'):
            with open(os.path.join(TEMPLATES_DIR, fname), 'r', encoding='utf-8') as f:
                raw = f.read()
            # Replace Flask static references before rendering
            raw = re.sub(
                r"\{\{\s*url_for\(['\"]static['\"],\s*filename=['\"]([^'\"]+)['\"]\)\s*\}\}",
                r"/static/\1",
                raw
            )
            template = env.from_string(raw)
            rendered = template.render(stripe_pk="pk_test_51A2XmONCbZx4JtzJIsWvWgOFm2z5z0GZbhM5qg9W7OZiJ6VJ6l0mZKpwBOYQxX5xSvO0vTmRX5SXc5Wn5pUcQkQk00LRdCCi5R")
            with open(os.path.join(BUILD_DIR, fname), 'w', encoding='utf-8') as f:
                f.write(rendered)

def fix_static_references():
    """Replace Flask static references with direct /static/... paths in HTML files."""
    for fname in os.listdir(BUILD_DIR):
        if fname.endswith('.html'):
            fpath = os.path.join(BUILD_DIR, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            # Replace {{ url_for('static', filename='...') }} with /static/...
            content = re.sub(
                r"\{\{\s*url_for\(['\"]static['\"],\s*filename=['\"]([^'\"]+)['\"]\)\s*\}\}",
                r"/static/\1",
                content
            )
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)

def main():
    create_build_dir()
    copy_static_files()
    render_templates()
    fix_static_references()
    # Check for CSS existence
    css_path = os.path.join(BUILD_DIR, 'static', 'css', 'style.css')
    if not os.path.exists(css_path):
        print("WARNING: build/static/css/style.css does not exist! CSS will not load.")

if __name__ == '__main__':
    main()
