import os
import subprocess
import argparse

def extract_deb_files(cve_dir):
    """
    Extract all .deb files in the vulnerable and patched directories and organize them under binaries.

    Parameters:
    cve_dir (str): The root directory containing the CVE-ID directory.
    """
    # Define the vulnerable and patch directories
    paths_to_process = ['vulnerable', 'patch']
    #breakpoint()
    # Iterate through both vulnerable and patch directories
    for version_dir in paths_to_process:
        version_path = os.path.join(cve_dir, version_dir)
        
        if not os.path.exists(version_path):
            print(f"{version_path} does not exist, skipping...")
            continue

        # Walk through the optimization level directories (opt0, opt1, etc.)
        for opt_dir in os.listdir(version_path):
            opt_path = os.path.join(version_path, opt_dir)
            if os.path.isdir(opt_path):
                # For each optimization directory (opt0, opt1, etc.)
                for file_name in os.listdir(opt_path):
                    if file_name.endswith(".deb"):
                        deb_path = os.path.join(opt_path, file_name)

                        # Create the binaries directory inside the current opt path
                        binaries_dir = os.path.join(opt_path, "binaries")
                        os.makedirs(binaries_dir, exist_ok=True)

                        # Create a directory named after the deb file (without extension)
                        deb_name = os.path.splitext(file_name)[0]
                        deb_extract_dir = os.path.join(binaries_dir, deb_name)
                        os.makedirs(deb_extract_dir, exist_ok=True)

                        # Extract the .deb file
                        try:
                            print(f"Extracting {deb_path} into {deb_extract_dir}...")
                            subprocess.run(['dpkg-deb', '-x', deb_path, deb_extract_dir], check=True)
                        except subprocess.CalledProcessError as e:
                            print(f"Error extracting {file_name}: {e}")
                        except Exception as e:
                            print(f"Unexpected error: {e}")

    print("Extraction process completed.")

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Extract .deb files in CVE directory structure.")
    # this is the structure of created deb files
    #CVE-ID/
    #    │
    #    ├── vulnerable/                # Directory containing vulnerable versions
    #    │   ├── opt0/                  # optimization level 0 for vulnerable version
    #    │   ├── opt1/                  # optimization level 1 for vulnerable version
    #    │   ├── opt2/                  # optimization level 2 for vulnerable version
    #    │   └── opt3/                  # optimization level 3 for vulnerable version
    #    │
    #    └── patch/                     # Directory containing patched versions
    #        ├── opt0/                  # optimization level 0 for patched version
    #        ├── opt1/                  # optimization level 1 for patched version
    #        ├── opt2/                  # optimization level 2 for patched version
    #        └── opt3/                  # optimization level 3 for patched version
    # give the directory of CVE-ID as an input to this script
    parser.add_argument('cve_dir', type=str, help="Path to the CVE-ID directory.")

    # Parse arguments
    args = parser.parse_args()

    # Call the extract function with the provided arguments
    extract_deb_files(args.cve_dir)

if __name__ == "__main__":
    main()
