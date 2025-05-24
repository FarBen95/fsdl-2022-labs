"""Sets up both local Jupyter and Google Colab notebooks for the FSDL course in the same state."""
import os
from pathlib import Path
import shutil
import sys
import subprocess
from subprocess import PIPE, Popen


try:  # check if we're in a git repo
    repo_dir = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, check=True).stdout.decode().strip()
    repo = Path(repo_dir).name
except subprocess.CalledProcessError:
    repo = os.environ.get("FSDL_REPO", "fsdl-text-recognizer-2022-labs")
        
branch = os.environ.get("FSDL_BRANCH", "main")
token = os.environ.get("FSDL_GHTOKEN")
prefix = token + "@" if token else ""

in_colab = "google.colab" in sys.modules


def _go():
    if in_colab: # create the repo and cd into it
        repo_root = Path("/") / "content" / repo
        os.chdir(repo_root.parent)
        
        shutil.rmtree(repo_root, ignore_errors=True)
        _clone_repo(repo, branch, prefix)
            
        os.chdir(repo_root)

        _install_dependencies_colab()

    else: # move to the repo root
        os.chdir(repo_dir)
        
        
def change_to_lab_dir(lab_idx=None):
    if lab_idx is None:
        return
    
    if not repo.endswith("labs"):
        return  # this is only needed in the labs repo

    lab_name = f"lab{str(lab_idx).zfill(2)}"
    cwd = Path.cwd().name
    if cwd != lab_name:  # if we're not in the lab directory
        if cwd != repo:  # check that we're in the repo root
            raise RuntimeError(f"run this command from the root of repo {repo}, not {cwd}")
        os.chdir(lab_name)  # and then cd into the lab directory


def _clone_repo(repo, branch, prefix):
    url = f"https://{prefix}github.com/full-stack-deep-learning/{repo}"
    subprocess.run(  # run git clone
        ["git", "clone", "--branch", branch, "-q", url], check=True)


def _install_dependencies_colab():
    subprocess.run( # directly pip install the prod requirements
        ["pip", "install", "--quiet", "-r", "requirements/prod.in"], check=True)

    # run a series of commands with pipes to pip install the dev requirements
    subprocess.run(
        ["sed 1d requirements/dev.in | grep -v '#' | xargs pip install --quiet"],
        shell=True, check=True)
        
    # reset pkg_resources list of requirements so gradio can ifner its version correctly
    import pkg_resources
    
    pkg_resources._initialize_master_working_set()
    

_go()