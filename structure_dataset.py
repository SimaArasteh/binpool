
import argparse
import os
import re
import shutil
from collections import defaultdict
def extract_paths_to_directory(directory_path):
    unique_names = set()
    file_names = []
    full_names = []
    file_paths = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_name  = file_path.split("/")[-1]
            file_parts = file_name.split("_")
            unique_names.add(file_parts[0])
            file_names.append(file_parts)
            full_names.append(file_name)
            file_paths.append(file_path)
    return unique_names, file_names, full_names, file_paths

def extract_structure(package_names, file_names):

    package_structure = defaultdict(list)
    
    unique_cves = set()
    for name in package_names:
        package_structure[name] = [[],[]]
        
        for file in file_names:
            if name == file[0]:
                if len(file) == 1:
                    pass 
                else:
                    patch_type = file[1]
                    opt_level = file[-1]
                    #print(name)
                    #print(patch_type)
                    #print(opt_level)
                    if patch_type == 'None':
                        # this is patch
                        package_structure[name][0].append('_'.join(file))
                    elif 'CVE' in patch_type:
                        # this is vulnerable
                        unique_cves.add(patch_type)
                        package_structure[name][1].append('_'.join(file))

    return unique_cves, package_structure

def extract_structure_based_cves (deb_filenames):
    unique_cves = set()
    cve_package = {}
    cve_pattern = r'CVE-\d{4}-\d{4,7}'
    for deb in deb_filenames:
        
        matches = re.findall(cve_pattern, deb)
        
        for item in matches:
            unique_cves.add(item)
    
    patch_pack = defaultdict(set)
    for cve in unique_cves:
        cve_package[cve] = [set(), set(), set(), ""]
        for name in deb_filenames:
            parts = name.split("_")
            pack_name = parts[0]
            opt_level = parts[-1]
            if cve in name:
                
                cve_package[cve][0].add(pack_name)
                cve_package[cve][1].add(opt_level)
                cve_package[cve][2].add(opt_level)
                cve_package[cve][3] = name
            
                
    return cve_package
    
def etxract_statistics(cve_structure):
    
    unique_packages = []

    unique_cves = list(cve_structure.keys())
    for cve in cve_structure:
        pack_ns = cve_structure[cve][0]
        unique_packages = unique_packages+list(pack_ns)
    
    print(len(set(unique_packages)))
    print(len(set(unique_cves)))
    

def create_directories_cves(cve_dict):
    base_dir = '/home/sima/binpool/binpool_dataset/'
    for cve_id in cve_dict.keys():
        # Define the path for each CVE directory
        cve_dir = os.path.join(base_dir, cve_id)
        
        # Create the CVE directory
        os.makedirs(cve_dir, exist_ok=True)
        
        # Define paths for 'vulnerable' and 'patch' directories inside each CVE directory
        vulnerable_dir = os.path.join(cve_dir, 'vulnerable')
        patch_dir = os.path.join(cve_dir, 'patch')
        
        # Create the 'vulnerable' and 'patch' directories
        os.makedirs(vulnerable_dir, exist_ok=True)
        os.makedirs(patch_dir, exist_ok=True)
        
        # Create the subdirectories 'opt0', 'opt1', 'opt2', 'opt3' inside both 'vulnerable' and 'patch'
        for opt in range(4):
            os.makedirs(os.path.join(vulnerable_dir, f'opt{opt}'), exist_ok=True)
            os.makedirs(os.path.join(patch_dir, f'opt{opt}'), exist_ok=True)

    

def etxract_cves_google_drive():
    cves = set()
    directory = "/workspaces/binpool/driver"
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            cve = file_path.split("/")[2]
            cves.add(cve)
    return cves

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="path to the deb files")
    parser.add_argument('path', type=str, help="path to deb files")

    args = parser.parse_args()
    unique_names, names, full_names , paths= extract_paths_to_directory(args.path)
    all_cves, pack_structure = extract_structure(unique_names, names)
    
    cve_dump = extract_structure_based_cves(full_names)
    #create_directories_cves(cve_dump)
    
    for cve in cve_dump:
        
        print(cve)
        pack_names = cve_dump[cve][0]
        for pack in pack_names:
            for opt in ['opt0', 'opt1', 'opt2', 'opt3']:
                #print(pack+"_None_"+opt)
                #print(pack+"_"+cve+"_"+opt)
                for path in paths:
                    if pack in path and '_None_' in path and opt in path:
                        destination_directory = "binpool_dataset/"+cve+"/patch/"+opt+"/"
                        os.makedirs(destination_directory, exist_ok=True)
                        shutil.copy(path, destination_directory)
                    elif pack in path and cve in path and opt in path:
                        destination_directory = "binpool_dataset/"+cve+"/vulnerable/"+opt+"/"
                        os.makedirs(destination_directory, exist_ok=True)
                        shutil.copy(path, destination_directory)

        

    
            
    