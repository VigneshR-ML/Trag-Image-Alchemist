import os
import shutil

def build():
    # Ensure static directory exists
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Copy necessary files to static directory
    # Add your build logic here
    print("Build completed successfully!")

if __name__ == "__main__":
    build()
