import pandas as pd
import os
import re
import requests
from time import sleep
from bs4 import BeautifulSoup
import wget
import subprocess
import tarfile
def create_debian_url(param_value):
    delimiter = "_"

    # Find the position of the first occurrence of the delimiter
    position = param_value.find(delimiter)

    # Extract the substrings before and after the delimiter
    substring1 = param_value[:position]
    substring2 = param_value[position + 1:]

    # Construct the URL
    url = 'https://snapshot.debian.org/package'
    final_url = f"{url}/{substring1}/{substring2}"
    return final_url

def crawl_webpage(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            hrefs = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.tar.xz')]
            return hrefs
        return []
    except requests.RequestException:
        return []

def download_file_with_wget(url, save_path):
    try:
        # Use the wget command to download the file
        subprocess.run(['wget', '-P', save_path, url], check=True)
        print(f"File downloaded successfully and saved to: {save_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading file: {e}")
    except FileNotFoundError:
        print("wget command not found. Make sure wget is installed.")
def ends_with_opt(file_name):
    # Regular expression to match _opt followed by a number from 0 to 3 at the end of the file name
    pattern = r"_opt[0-3]$"
    return re.search(pattern, file_name) is not None

def extract_debian_files(cve_directory):
    for dirpath, dirnames, filenames in os.walk(cve_directory):
        count = 1  # Counter to create unique directory names
        for file in filenames:
            if file.endswith('.debian.tar.xz'):
                # Create a unique directory name for each .debian.tar.xz file
                unique_dir_name = f'debian{count}_extracted'
                extract_dir = os.path.join(dirpath, unique_dir_name)
                os.makedirs(extract_dir, exist_ok=True)

                # Full path to the .debian.tar.xz file
                file_path = os.path.join(dirpath, file)

                # Extract the .debian.tar.xz file
                with tarfile.open(file_path, "r:xz") as tar:
                    tar.extractall(path=extract_dir)

                print(f'Extracted {file} into {extract_dir}')
                count += 1  # Increment the counter for the next unique directory


def extract_tar_to_debfiles(tar_path):
    """
    Extracts a tar file into a 'debfiles' directory in the current directory using the 'tar' command.

    :param tar_path: Path to the tar file
    """
    tar_parts = tar_path.split("/")
    tar_main = '/'.join(tar_parts[:-1])
    #print(tar_main)
    # Create 'debfiles' directory in the current directory
    debfiles_dir = os.path.join(tar_main, "debfiles")
    os.makedirs(debfiles_dir, exist_ok=True)

    try:
        # Run the 'tar' command to extract the tar file into the 'debfiles' directory
        subprocess.run(["tar", "-xf", tar_path, "-C", debfiles_dir], check=True)
        print(f"Successfully extracted {tar_path} to {debfiles_dir}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while extracting {tar_path} using the 'tar' command: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
def extract_debfiles_to_bin(path_deb):
    #breakpoint()
    directory_name = path_deb.split("/")[-1].replace('.deb', '')
    directory_parts = path_deb.split("/")[:-1]
    directory_path = "/".join(directory_parts)
    directory_path = directory_path+"/bins/"
    os.makedirs(directory_path, exist_ok=True)
    deb_extract_dir = os.path.join(directory_path, directory_name)
    #print(deb_extract_dir)
    #os.makedirs(deb_extract_dir, exist_ok=True)
    try:
        print(f"Extracting {path_deb} into {deb_extract_dir}...")
        subprocess.run(['dpkg-deb', '-x', path_deb, deb_extract_dir], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error extracting {path_deb}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")



if __name__ == "__main__":
    '''file_path = 'binpool.csv'
    df = pd.read_csv(file_path)
    root_dir = "CVE_Directories/"
    cves = set()
    for root, dirs, _ in os.walk(root_dir):
        for dir_name in dirs:
            path = os.path.join(root, dir_name)
            cves.add(path.split("/")[1])
            
    filtered_df = df[df['cve'].isin(list(cves))]

    # Extract only the CVE and Debian Package columns
    result_df = filtered_df[['cve', 'fix_version']]
    #url = create_debian_url(result_df)
    #print(result_df)
    main_address = "https://snapshot.debian.org"
    for index, row in result_df.iterrows():
        cve = row['cve']
        fix_version = row['fix_version']
        #print(f"CVE: {cve}, Fix Version: {fix_version}")
        url = create_debian_url(fix_version)
        #print(url)
        hrefs = crawl_webpage(url)
        final_url =""
        try:
            if len(hrefs) > 1:
                final_url = main_address+hrefs[1]
            else:
                #print(cve)
                #print(fix_version)
                final_url = main_address+hrefs[0]
            print(final_url)
            
            
        except:
            continue 

        if final_url != "":
            print(cve)
            path_to_save = "CVE_Directories/"+cve
            print(final_url)
            download_file_with_wget(final_url, path_to_save)'''
    
    
    #extract_debian_files('CVE_Directories/')
    root_dir = "/home/sima/binpool/binpool_dataset/"
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            path = os.path.join(root, file)
            
            if '/patch/' in path or '/vulnerable/' in path:
                if ends_with_opt(path):
                    extract_tar_to_debfiles(path)
    
    root_dir = "/home/sima/binpool/binpool_dataset/"
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            path = os.path.join(root, file)
            if '/debfiles/' in path:
                extract_debfiles_to_bin(path)
