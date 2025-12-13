import subprocess
import zipfile
import requests
import os
import sys
import shutil
import platform
import stat

PY4GODOTPATH = "py4godot_latest/py4godot"
PYTHON_VERSION = "3.12.4"
def download_and_extract_latest_release(repo_owner, repo_name, download_dir="."):
    """
    Download and extract the latest release from a GitHub repository

    Args:
        repo_owner (str): The owner of the repository
        repo_name (str): The name of the repository
        download_dir (str): Directory to save and extract the downloaded file(s)
    """
    # Create the download directory if it doesn't exist
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    else:
        return # We assue, py4godot was already downloaded
    # Get the latest release information using GitHub API
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    headers = {"Accept": "application/vnd.github.v3+json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        release_data = response.json()
        release_tag = release_data["tag_name"]
        release_assets = release_data["assets"]

        if not release_assets:
            print(f"No assets found for the latest release ({release_tag})")
            return

        zip_files = []

        # Download each asset
        for asset in release_assets:
            asset_name = asset["name"]
            asset_url = asset["browser_download_url"]

            print(f"Downloading {asset_name} from release {release_tag}...")

            download_path = os.path.join(download_dir, asset_name)
            asset_response = requests.get(asset_url, stream=True)
            asset_response.raise_for_status()

            with open(download_path, "wb") as f:
                for chunk in asset_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Downloaded {asset_name} to {download_path}")

            # Add zip files to list for extraction
            if asset_name.endswith('.zip'):
                zip_files.append(download_path)

        # Extract all downloaded zip files
        for zip_path in zip_files:
            extract_dir = os.path.join(download_dir, os.path.splitext(os.path.basename(zip_path))[0])
            print(f"Extracting {zip_path} to {extract_dir}...")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            print(f"Successfully extracted {zip_path}")

        print("Moving py4godot to right location...")
        shutil.move("py4godot_latest/py4godot/install_dir/addons/py4godot", "py4godot_latest/py4godot")
        if platform.system() == "Darwin":
            # Get current permissions
            file_path = f"py4godot_latest/py4godot/py4godot/cpython-{PYTHON_VERSION}-darwin64/python/bin/python3"
            st = os.stat(file_path)

            # Add executable permissions for the user, group, and others
            os.chmod(file_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        elif platform.system() == "Linux":
            # Get current permissions
            file_path = f"py4godot_latest/py4godot/py4godot/cpython-{PYTHON_VERSION}-linux64/python/bin/python3"
            st = os.stat(file_path)

            # Add executable permissions for the user, group, and others
            os.chmod(file_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


        print(f"Successfully downloaded and extracted all assets from release {release_tag}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the latest release: {e}")
        sys.exit(1)
    except zipfile.BadZipFile as e:
        print(f"Error extracting zip file: {e}")
        sys.exit(1)


def init_projects():
    projects = ["dodge_the_creeps", "heightmap", "button_demo", "python-class-instantiation", "godot-pytorch",
                "truck_town", "godot-python-interaction", "platformer"]
    for project in projects:
        print((f"Copying py4godot into {project}..."))
        copy_py4godot(project)
        print(f"Installing packages for {project}...")
        install_requirements(project)


def copy_py4godot(path):
    if (os.path.exists(path + "/addons")):
        os.makedirs(path + "/addons", exist_ok=True)
    shutil.copytree(PY4GODOTPATH, path + "/addons", dirs_exist_ok=True)

def install_requirements(path):
    if not os.path.exists(path + "/requirements.txt"):
        print("No packages to install")
        return
    if platform.system() == "Windows":
        run_command_and_print([f"{path}/addons/py4godot/cpython-{PYTHON_VERSION}-windows64/python/python.exe", f"{path}/addons/py4godot/get_pip.py"])

        run_command_and_print([
            f"{path}/addons/py4godot/cpython-{PYTHON_VERSION}-windows64/python/python.exe",
            "-m", "pip", "install", "-r", f"{path}/requirements.txt"
        ])
    elif platform.system() == "Linux":
        os.chmod(f"{path}/addons/py4godot/cpython-{PYTHON_VERSION}-linux64/python/bin/python3", 0o777)
        run_command_and_print([f"{path}/addons/py4godot/cpython-{PYTHON_VERSION}-linux64/python/bin/python3", f"{path}/addons/py4godot/get_pip.py"])
        run_command_and_print([
            f"{path}/addons/py4godot/cpython-{PYTHON_VERSION}-linux64/python/bin/python3",
            "-m", "pip", "install", "-r", f"{path}/requirements.txt"])
    elif platform.system() == "Darwin":
        run_command_and_print([f"{path}/addons/py4godot/cpython-{PYTHON_VERSION}-darwin64/python/bin/python3", f"{path}/addons/py4godot/get_pip.py"])
        run_command_and_print([
            f"{path}/addons/py4godot/cpython-{PYTHON_VERSION}-darwin64/python/bin/python3",
            "-m", "pip", "install", "-r", f"{path}/requirements.txt"])


def run_command_and_print(cmd):
    print("Running: " + " ".join(cmd))
    subprocess.run(cmd)

if __name__ == "__main__":
    # Set the repository details for py4godot
    repo_owner = "niklas2902"
    repo_name = "py4godot"

    # Set download directory
    download_dir = "py4godot_latest"

    # Download and extract the latest release
    download_and_extract_latest_release(repo_owner, repo_name, download_dir)
    init_projects()
