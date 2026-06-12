import os
import subprocess
import argparse
from datetime import datetime

# Define the paths to all your active DRIFT/Forge repositories
REPOS = {
    "AI_Forge_Protocol": "/home/crexs/ai_forge_protocol",
    "INFJ_Bot": "/home/crexs/infj_bot",
    "Lotus_Academy": "/home/crexs/lotus-academy",
    "My_Site": "/home/crexs/my-site"
}

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def run_cmd(cmd, cwd):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, shell=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def check_status():
    """Check the git status of all repositories."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== DRIFT GITHUB OBSERVATORY ==={Colors.ENDC}\n")
    for name, path in REPOS.items():
        if not os.path.exists(path):
            print(f"{Colors.WARNING}⚠️  {name}: Path not found ({path}){Colors.ENDC}")
            continue
            
        code, out, err = run_cmd("git status --short", path)
        if code != 0:
            print(f"{Colors.FAIL}❌ {name}: Git Error - {err}{Colors.ENDC}")
            continue
            
        if not out:
            print(f"{Colors.OKGREEN}✅ {name}: Clean (No changes){Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠️  {name}: Uncommitted changes detected{Colors.ENDC}")
            for line in out.split('\n'):
                print(f"      {line}")
    print("\n")

def sync_repos():
    """Pull the latest changes from origin for all repos."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== SYNCING ALL REPOSITORIES ==={Colors.ENDC}\n")
    for name, path in REPOS.items():
        if not os.path.exists(path):
            continue
        print(f"Pulling {Colors.OKCYAN}{name}{Colors.ENDC}...")
        code, out, err = run_cmd("git pull origin main || git pull origin master", path)
        if code == 0:
            print(f"{Colors.OKGREEN}  -> Success!{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}  -> Failed: {err}{Colors.ENDC}")
    print("\n")

def push_all(message=None):
    """Commit and push all changes across all repos."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== GLOBAL PUSH INITIATED ==={Colors.ENDC}\n")
    
    if not message:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"chore: DRIFT automated system sync [{timestamp}]"

    for name, path in REPOS.items():
        if not os.path.exists(path):
            continue
            
        # Check if there are changes first
        code, out, _ = run_cmd("git status --short", path)
        if not out:
            print(f"{Colors.OKGREEN}⏭️  {name}: Skipped (No changes to push){Colors.ENDC}")
            continue
            
        print(f"Pushing {Colors.OKCYAN}{name}{Colors.ENDC}...")
        
        # Add all
        run_cmd("git add .", path)
        
        # Commit
        code, out, err = run_cmd(f'git commit -m "{message}"', path)
        if code != 0 and "nothing to commit" not in out:
            print(f"{Colors.FAIL}  -> Commit Failed: {err}{Colors.ENDC}")
            continue
            
        # Push
        code, out, err = run_cmd("git push origin HEAD", path)
        if code == 0:
            print(f"{Colors.OKGREEN}  -> Push Successful!{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}  -> Push Failed: {err}{Colors.ENDC}")
    print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DRIFT Automated GitHub Manager")
    parser.add_argument("action", choices=["status", "sync", "push"], help="The action to perform")
    parser.add_argument("-m", "--message", type=str, help="Commit message for 'push' action")
    
    args = parser.parse_args()
    
    if args.action == "status":
        check_status()
    elif args.action == "sync":
        sync_repos()
    elif args.action == "push":
        push_all(args.message)
