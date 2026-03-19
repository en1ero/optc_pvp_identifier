import os
import subprocess


class SubmoduleError(Exception):
    """Custom exception for submodule operations"""
    pass


def run_git_command(cwd, *args):
    """Run a git command in the given directory"""
    try:
        result = subprocess.run(
            ['git'] + list(args),
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise SubmoduleError(f"Git command failed: {e.stderr.strip()}")


def is_git_repo(path):
    """Check if path is a git repository"""
    git_path = os.path.join(path, '.git')
    return os.path.isdir(git_path) or os.path.isfile(git_path)


def checkout_submodule_at_date(submodule_path, date_str, branch="master"):
    """
    Checkout the submodule at the latest commit before the given date.
    
    Args:
        submodule_path: Path to the submodule directory
        date_str: Date string in YYYY-MM-DD format
        branch: Remote branch to fetch from (default: master)
    
    Returns:
        The commit hash that was checked out
    
    Raises:
        SubmoduleError: If checkout fails
    """
    if not os.path.exists(submodule_path):
        raise SubmoduleError(
            f"Submodule path does not exist: {submodule_path}. "
            "Please ensure the submodule is initialized."
        )
    
    if not is_git_repo(submodule_path):
        raise SubmoduleError(f"Not a git repository: {submodule_path}")
    
    print(f"Fetching latest from origin/{branch}...")
    run_git_command(submodule_path, 'fetch', 'origin', branch)
    
    print(f"Finding commit before {date_str}...")
    commit_hash = run_git_command(
        submodule_path,
        'rev-list',
        '-n', '1',
        f'--before={date_str}',
        f'origin/{branch}'
    )
    
    if not commit_hash:
        raise SubmoduleError(
            f"No commits found before {date_str} on origin/{branch}. "
            f"Try an earlier date."
        )
    
    print(f"Checking out commit {commit_hash[:8]}...")
    run_git_command(submodule_path, 'checkout', commit_hash)
    
    return commit_hash


def get_current_submodule_commit(submodule_path):
    """
    Get the current commit hash of the submodule.
    
    Returns:
        The commit hash, or None if not in a git repo
    """
    if not is_git_repo(submodule_path):
        return None
    
    try:
        return run_git_command(submodule_path, 'rev-parse', 'HEAD')
    except SubmoduleError:
        return None


def init_submodule(submodule_path, url=None):
    """
    Initialize and clone a submodule.
    
    Args:
        submodule_path: Path where submodule should be cloned
        url: Repository URL (if not already configured)
    
    Returns:
        True if successful
    """
    if is_git_repo(submodule_path):
        print(f"Submodule already initialized at {submodule_path}")
        return True
    
    if not url:
        raise SubmoduleError("No URL provided and submodule not initialized")
    
    print(f"Cloning submodule from {url}...")
    os.makedirs(submodule_path, exist_ok=True)
    run_git_command(
        os.path.dirname(submodule_path) or '.',
        'submodule', 'add', url, submodule_path
    )
    return True
