#!/usr/bin/env python3
import os
import sys
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

def run_command(cmd, cwd=None):
    """Run a shell command and stream output in real time."""
    logging.info(f"Running command: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    for line in process.stdout:
        logging.info(line.strip())
    process.wait()
    if process.returncode != 0:
        logging.error(f"Command failed with exit code {process.returncode}")
        sys.exit(process.returncode)

def main():
    # 1. Read service account path from env var
    sa_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_TRAG_IMAGE_ALCHEMIST")
    if not sa_path:
        logging.error("Environment variable FIREBASE_SERVICE_ACCOUNT_TRAG_IMAGE_ALCHEMIST is not set.")
        sys.exit(1)
    if not os.path.isfile(sa_path):
        logging.error(f"Service account file not found at: {sa_path}")
        sys.exit(1)

    # 2. Set GOOGLE_APPLICATION_CREDENTIALS for Firebase CLI auth
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path
    logging.info(f"Set GOOGLE_APPLICATION_CREDENTIALS to {sa_path}")

    # 3. Run your build step before deploy
    #    (as per your GitHub Action prompt: `npm ci && npm run build`)
    run_command(["npm", "ci"])
    run_command(["npm", "run", "build"])

    # 4. Deploy to Firebase Hosting
    #    You can customize the --only flag to include functions, firestore, etc.
    firebase_args = ["firebase", "deploy", "--only", "hosting"]
    # If you need to deploy functions as well, uncomment:
    # firebase_args = ["firebase", "deploy", "--only", "hosting,functions"]

    run_command(firebase_args)

    logging.info("✅ Deployment complete.")

if __name__ == "__main__":
    main()
