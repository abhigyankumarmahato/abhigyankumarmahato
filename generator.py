import os
import sys
import random
import subprocess
from datetime import datetime, timedelta

# Realistic developer commit messages
COMMIT_MESSAGES = [
    "feat: implement user authentication flow",
    "fix: resolve race condition in database queries",
    "refactor: clean up utility functions",
    "docs: update setup instructions in README",
    "test: add unit tests for api endpoints",
    "style: format imports and fix linting warnings",
    "chore: update dependency versions",
    "feat: integrate payment gateway API",
    "fix: correct layout spacing on mobile views",
    "perf: optimize query performance using indexing",
    "feat: add dark mode theme support",
    "refactor: modularize routes and middleware",
    "fix: handle null pointer exceptions in parser",
    "docs: add API documentation comments",
    "feat: implement export to CSV feature",
    "test: verify edge cases in password validator",
    "fix: resolve memory leak in websocket listener",
    "feat: add logging middleware for request telemetry",
    "chore: clean up deprecated assets",
    "refactor: extract validation logic into separate helper"
]

def check_git():
    """Verify git is installed and initialize if necessary."""
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Git is not installed or not in your system PATH.")
        sys.exit(1)

    # Initialize git repo if not already in one
    if not os.path.exists(".git"):
        print("Initializing new Git repository...")
        subprocess.run(["git", "init"], check=True)
        # Create a default branch name if needed
        subprocess.run(["git", "checkout", "-b", "main"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print("Existing Git repository detected.")

def verify_git_config():
    """Verify that user email and name are configured, and remind user."""
    try:
        user_email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, check=True).stdout.strip()
        user_name = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError:
        user_email = ""
        user_name = ""

    print("\n" + "=" * 60)
    print("GIT CONFIGURATION STATUS")
    print(f"Current Git Name:  {user_name if user_name else 'NOT SET'}")
    print(f"Current Git Email: {user_email if user_email else 'NOT SET'}")
    print("=" * 60)
    
    if not user_email or not user_name:
        print("\nWARNING: Git name or email is not set locally.")
        print("GitHub associates commits with your profile using your primary GitHub email.")
        email_input = input("Enter your GitHub Email to configure locally (or press Enter to skip): ").strip()
        name_input = input("Enter your GitHub Name to configure locally (or press Enter to skip): ").strip()
        
        if email_input:
            subprocess.run(["git", "config", "user.email", email_input], check=True)
            user_email = email_input
        if name_input:
            subprocess.run(["git", "config", "user.name", name_input], check=True)
            user_name = name_input
            
    print("\nNOTE: Ensure the email matches the one listed in your GitHub Account Settings.")
    print("Otherwise, GitHub will NOT count these commits on your contribution graph.")
    print("=" * 60 + "\n")
    return user_email

def generate_commits(days=365, max_commits_per_day=5, weekday_prob=0.7, weekend_prob=0.2):
    """Generate backdated commits."""
    check_git()
    verify_git_config()
    
    start_date = datetime.now() - timedelta(days=days)
    total_commits = 0
    
    # We will write to 'contributions.txt' to perform actual modifications
    filename = "contributions.txt"
    
    print(f"Generating realistic commit history for the past {days} days...")
    print("Please wait...")

    for i in range(days):
        current_date = start_date + timedelta(days=i)
        
        # Decide if we commit on this day
        is_weekend = current_date.weekday() >= 5
        prob = weekend_prob if is_weekend else weekday_prob
        
        if random.random() > prob:
            continue
            
        # Determine number of commits for this day
        num_commits = random.randint(1, max_commits_per_day)
        
        for commit_idx in range(num_commits):
            # Generate a random time of day (e.g., between 9:00 AM and 11:00 PM)
            hour = random.randint(9, 22)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            commit_time = current_date.replace(hour=hour, minute=minute, second=second)
            
            # Format date as ISO string
            date_str = commit_time.isoformat()
            
            # Modify the dummy file to ensure a real change is recorded
            content = f"Contribution entry {total_commits + 1} at {date_str}\n"
            with open(filename, "a") as f:
                f.write(content)
                
            # Stage the file
            subprocess.run(["git", "add", filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            # Choose a random realistic commit message
            message = random.choice(COMMIT_MESSAGES)
            
            # Commit with backdated timestamp environment variables
            env = os.environ.copy()
            env["GIT_AUTHOR_DATE"] = date_str
            env["GIT_COMMITTER_DATE"] = date_str
            
            subprocess.run(
                ["git", "commit", "-m", message],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            
            total_commits += 1
            
        # Print progress update every 30 days
        if i % 30 == 0:
            print(f"Processed day {i}/{days}... Total commits generated: {total_commits}")
            
    print("\n" + "=" * 60)
    print("SUCCESS: Commits generation completed!")
    print(f"Total Commits Created: {total_commits}")
    print("Next Steps:")
    print("  1. Create a NEW public or private repository on GitHub (e.g., 'my-contributions').")
    print("  2. Add your GitHub remote:")
    print("     git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git")
    print("  3. Rename default branch (optional but standard):")
    print("     git branch -M main")
    print("  4. Push your commits to GitHub:")
    print("     git push -u origin main")
    print("\nOnce pushed, GitHub will scan your commits and display them on your contribution graph!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="GitHub Contribution Generator")
    parser.add_argument("--days", type=int, default=365, help="Number of days to backdate (default: 365)")
    parser.add_argument("--max-commits", type=int, default=5, help="Max commits per active day (default: 5)")
    parser.add_argument("--weekday-prob", type=float, default=0.7, help="Probability of commit on weekday (default: 0.7)")
    parser.add_argument("--weekend-prob", type=float, default=0.2, help="Probability of commit on weekend (default: 0.2)")
    
    args = parser.parse_args()
    
    generate_commits(
        days=args.days,
        max_commits_per_day=args.max_commits,
        weekday_prob=args.weekday_prob,
        weekend_prob=args.weekend_prob
    )
