import os
import shutil
import re

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

def copy_templates():
    """Copy and (if desired) rename templates into build/"""
    mapping = {
        'landing.html': 'index.html',  # root
        'index.html':   'editor.html',
        'pricing.html': 'pricing.html',
        'success.html': 'success.html',
        '404.html':     '404.html'
    }
    for src_name, dst_name in mapping.items():
        src = os.path.join(TEMPLATES_DIR, src_name)
        dst = os.path.join(BUILD_DIR, dst_name)
        if os.path.exists(src):
            shutil.copy2(src, dst)

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
    copy_templates()
    fix_static_references()

if __name__ == '__main__':
    main()
