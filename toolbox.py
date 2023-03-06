import os
import winreg
import subprocess
import win32net
import time
import json
import urllib.request

start_time = time.time()

def start_timer():
    """
    Starts a timer for the overall run time of the Python application.
    """
    global start_time
    start_time = time.time()

def is_application_installed(app_name):
    """
    Checks if a given application is installed on Windows.

    Parameters:
    app_name (str): The name of the application to check.

    Returns:
    bool: True if the application is installed, False otherwise.
    """
    try:
        # Open the uninstall registry key.
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall")

        # Iterate over the subkeys in the uninstall registry key.
        for i in range(winreg.QueryInfoKey(key)[0]):
            subkey_name = winreg.EnumKey(key, i)

            # Open each subkey and check if it contains the application name.
            subkey = winreg.OpenKey(key, subkey_name)
            try:
                display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                if app_name in display_name:
                    return True
            except:
                pass

        return False
    except Exception as e:
        print(f"Error checking if application {app_name} is installed: {e}")
        return False

def write_registry_key(key_path, value_name, value_data):
    """
    Writes a value to a Windows registry key.

    Parameters:
    key_path (str): The path of the registry key to write to.
    value_name (str): The name of the registry value to write.
    value_data (str): The data to write to the registry value.

    Returns:
    bool: True if the write operation was successful, False otherwise.
    """
    try:
        # Open the registry key for writing.
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)

        # Write the value to the registry.
        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value_data)

        # Close the registry key.
        winreg.CloseKey(key)

        return True
    except Exception as e:
        print(f"Error writing registry key {key_path} with value {value_data}: {e}")
        return False

def download_and_run_file(url, file_path, username, password):
    """
    Downloads a file from a URL and runs it as an administrator with credentials.

    Parameters:
    url (str): The URL of the file to download.
    file_path (str): The path to save the downloaded file.
    username (str): The username of the account with administrator privileges.
    password (str): The password of the account with administrator privileges.

    Returns:
    bool: True if the file is downloaded and run successfully, False otherwise.
    """
    try:
        # Download the file using the URL and save it to the file path.
        subprocess.run(["powershell", "-Command", f"(New-Object System.Net.WebClient).DownloadFile('{url}', '{file_path}')"], check=True)

        # Run the file as an administrator with the specified username and password.
        net_resource = {
            "unc": file_path,
            "username": username,
            "password": password
        }
        net_use_command = f"net use {net_resource['unc']} /user:{net_resource['username']} {net_resource['password']}"
        subprocess.run(net_use_command, check=True, shell=True)

        run_command = f"runas /user:{username} /savecred \"{file_path}\""
        subprocess.run(run_command, check=True, shell=True)

        return True
    except Exception as e:
        print(f"Error downloading and running file: {e}")
        return False


end_time = time.time()
total_time = end_time - start_time
print(f"Application run time: {total_time:.2f} seconds")


def check_latest_version(repo_url, app_name, current_version):
    """
    Checks if the app is on the latest version based on a JSON file located on GitHub.com.

    Parameters:
    repo_url (str): The URL of the GitHub repository containing the JSON file.
    app_name (str): The name of the app to check the version for.
    current_version (str): The current version of the app.

    Returns:
    tuple: A tuple containing the new version number and date if the app is not up to date; otherwise, None.
    """
    try:
        # Construct the URL of the JSON file.
        json_url = f"{repo_url}/releases/latest/download/{app_name}.json"

        # Download the JSON file.
        with urllib.request.urlopen(json_url) as url:
            data = json.loads(url.read().decode())

        # Check if the app is up to date.
        new_version = data["version"]
        if new_version != current_version:
            new_date = data["date"]
            return (new_version, new_date)

        return None
    except Exception as e:
        print(f"Error checking latest version: {e}")
        return None






