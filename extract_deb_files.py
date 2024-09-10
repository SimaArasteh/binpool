import os
import subprocess
import argparse

def extract_deb_files(deb_dir, extract_to):
    """
    Extract all .deb files from a given directory into their respective subdirectories.

    Parameters:
    deb_dir (str): The directory containing the .deb files.
    extract_to (str): The directory where extracted files will be stored.
    """
    # Create the destination directory if it doesn't exist
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    # List all files in the directory
    for file_name in os.listdir(deb_dir):
        if file_name.endswith(".deb"):
            deb_path = os.path.join(deb_dir, file_name)
            output_dir = os.path.join(extract_to, file_name[:-4])  # Remove the .deb extension

            # Create a directory for this .deb file
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Extract the .deb file
            try:
                print(f"Extracting {file_name} into {output_dir}")
                subprocess.run(['dpkg-deb', '-x', deb_path, output_dir], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error extracting {file_name}: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")


def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Extract .deb files into subdirectories named after the file.")
    parser.add_argument('deb_dir', type=str, help="Directory containing .deb files.")
    parser.add_argument('extract_to', type=str, help="Directory to extract the .deb files into.")

    # Parse arguments
    args = parser.parse_args()

    # Call the extract function with the provided arguments
    extract_deb_files(args.deb_dir, args.extract_to)



if __name__ == "__main__":
    main()