import argparse
import os
import sys
import subprocess
import tarfile
import re

def ends_with_opt(file_name):
    # Regular expression to match _opt followed by a number from 0 to 3 at the end of the file name
    pattern = r"_opt[0-3]$"
    return re.search(pattern, file_name) is not None

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




def main():
    parser = argparse.ArgumentParser(description="Process path to BinPool dataset directory.")
    parser.add_argument(
        'dataset_path',
        type=str,
        help='Path to the binpool_dataset directory'
    )
    
    args = parser.parse_args()
    dataset_path = args.dataset_path

    if not os.path.isdir(dataset_path):
        print(f"Error: '{dataset_path}' is not a valid directory.")
        sys.exit(1)

    print(f"Dataset directory: {dataset_path}")

       
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            path = os.path.join(root, file)
            
            if '/patch/' in path or '/vulnerable/' in path:
                if ends_with_opt(path):
                    extract_tar_to_debfiles(path)
    
    
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            path = os.path.join(root, file)
            if '/debfiles/' in path:
                extract_debfiles_to_bin(path)

if __name__ == "__main__":
    main()
