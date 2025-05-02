import subprocess
from build import main as build_site

def run_command(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline, b''):
        print(line.decode().rstrip())
    proc.stdout.close()
    return proc.wait()

def main():
    print("🏗️ Building site…")
    build_site()

    print("🚀 Deploying to Firebase Hosting…")
    code = run_command("firebase deploy --only hosting")
    if code == 0:
        print("✅ Deployment successful!")
    else:
        print("❌ Deployment failed.")
        exit(code)

if __name__ == "__main__":
    main()
