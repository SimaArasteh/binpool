import json
import argparse
import os 
import re
import joblib
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from collections import defaultdict
import pandas as pd
import requests
import subprocess
from elftools.elf.elffile import ELFFile
import elftools
def run_dget_in_directory(dsc_url, download_dir):


    try:
        subprocess.run(
            ["dget", "-u", "--insecure", dsc_url],
            check=True,
            cwd=download_dir
        )
        print(f"Downloaded to: {os.path.abspath(download_dir)}")
    except Exception as e:
        print(f"Failed to run dget: {e}")
        pass  # just skip, no 'continue' here

def get_first_dsc_link(url):
    base_url = "https://snapshot.debian.org"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.endswith(".dsc"):
            return base_url + href

    return None 

def extract_all_cwe_ids(cve_id):
    url = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    cwe_table = soup.find("table", {"data-testid": "vuln-CWEs-table"})
    if not cwe_table:
        return []

    # Find all <td> tags with CWE links
    cwe_links = cwe_table.find_all("td", {"data-testid": lambda x: x and x.startswith("vuln-CWEs-link-")})

    # Extract and clean CWE IDs
    cwe_ids = []
    for td in cwe_links:
        a_tag = td.find("a")
        if a_tag and "CWE-" in a_tag.text:
            cwe_ids.append(a_tag.text.strip())

    return list(set(cwe_ids))  # Remove duplicates if any

def extract_binpool_info(dataset_path):
    list_cves = set()
    list_deb_files = set()
    list_deb_names = []
    
    for root, dirs, files in os.walk(dataset_path):
        for filename in files:
            full_path = os.path.join(root, filename)
            cve = full_path.split("/")[1]
            list_cves.add(cve)
            #list_deb_names = list_deb_names + return_package_name(cve)
            if "/debfiles/" in full_path and full_path.endswith(".deb"):
                deb_file = full_path.split("/")[-1]
                
                list_deb_files.add(deb_file)
                #print(deb_file)
                
                
                #list_deb_names.add(parts[0])
                
                
    print(len(list_deb_files))
    print(len(list_cves))
    map_cve_pack, map_cve_cwe = return_package_name(list_cves)
    print(len(set(map_cve_pack.values())))
    #print(len(set(list_deb_names)))
    list_cwes = []

    for cv in map_cve_cwe:
        list_cwes = list_cwes +map_cve_cwe[cv]

    #print(len(set(list_cwes)))

    joblib.dump(list_deb_files, "metadata/list_deb_files.pkl")
    joblib.dump(list_cves, "metadata/list_cves.pkl")
    joblib.dump(map_cve_pack, "metadata/map_cve_pack.pkl")
    joblib.dump(map_cve_cwe, "metadata/map_cwe_pack.pkl")

def extract_function_names(dataset_path):
    functions = []
    map_cve_funcs = {}
    for root, dirs, files in os.walk(dataset_path):
        for filename in files:
            full_path = os.path.join(root, filename)
            cve = full_path.split("/")[1]
            if full_path.endswith(".patch") and 'opt0' in full_path:
                print(cve)
                
                file_infos, file_lines = parse_patch_file(full_path)
                returned_funcs = extract_function_info(file_lines, file_infos, 's', full_path)
                #print(file_infos)
                funcs = []
                for fi, fn in returned_funcs:
                    print(fi)
                    if fn is not None:
                        funcs.append(fn)
                print(funcs)
                map_cve_funcs[cve] = returned_funcs
                print("*************************")
                
    return map_cve_funcs

def find_lines_for_diff(patch_lines, g_lines):
    i = 0 
    g_ls = {}
    while i < len(g_lines):
        if i+1 < len(g_lines):
            start = g_lines[i]
            end = g_lines[i+1]
            g_ls[start] = patch_lines[start:end]
        else:
            start = g_lines[i]
            end = None
            for l in patch_lines[start:]:
                if l.startswith('---'):
                    end = patch_lines.index(l)
            if end is None:
                end = len(patch_lines)
            g_ls[start] = patch_lines[start:end]
        i+=1
    return g_ls
def find_function(git_diff_line):
    if "(" in git_diff_line:
        parts = git_diff_line.split("(")[0]
        func = parts.strip().split(" ")[-1]
        return func
    return None

def find_patch_lines (diff_line):
    match = re.search(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@', diff_line)
    if match:
        # Convert captured groups to integers and format them into the list as specified
        removed = [-int(match.group(1)), int(match.group(2))]
        added = [+int(match.group(3)), int(match.group(4))]
        return [removed, added]
    else:
        return None


def extract_function_info(lis , file_info, status, path_to_patch):
    files_funcs = {}
    funcs = set()
    files = set()
    cve = path_to_patch.split("/")[1]
    cve_files_funcs = {}
    list_file_funcs = []
    for file_idx in file_info:
        file_name = lis[file_idx]
        f_name = file_name.split(" ")[1].split("\t")[0].strip()
        f_name = f_name[2:]
        files.add(f_name)
        f_last_name = f_name.split("/")[-1]
        print(f_last_name)
        git_lines = file_info[file_idx]
        modifided_lines = find_lines_for_diff(lis, git_lines)
        for l in git_lines:
            git_line = lis[l]
            git_line = git_line.strip()
            diff_lines = modifided_lines[l]
            #print(git_line)
            func_name = find_function(git_line)
            changed_lines = find_patch_lines(git_line)
            
            #print(changed_lines)
            target_line = None

            list_file_funcs.append((f_name, func_name))
           
            if func_name is not None:
                
                funcs.add(func_name)
            else: #when function name does not apear on the git diff
                root_dir = "/home/sima/binpool/binpool_artifact/"+cve
                for dirpath, dirnames, filenames in os.walk(root_dir):
                    for filename in filenames:
                        full_path = os.path.join(dirpath, filename)
                        if  ".pc/" not in full_path and full_path.split("/")[-1] == f_last_name:
                            if full_path.endswith(".c") or full_path.endswith(".cpp") or full_path.endswith(".java"):
                                try:
                                    with open(full_path, 'r') as f:
                                        data = f.readlines()
                                        print(full_path)
                                        #breakpoint()
                                        indexes = define_fountion_bounderies(data)
                                        function_name = find_function_name(diff_lines, data ,indexes, full_path)
                                        print(function_name)
                                        list_file_funcs.append((f_name, function_name))
                                    
                                except:
                                    continue
                                    
                                    

   
    #print(cve_files_funcs)
    return list_file_funcs

def find_function_name(diff_lines, file_lines, function_indexes, path):

    """
        to find the function name when it does not apear on the git diff
        we search for the changed lines in the git diff and map in to the
        function body to understand which funciton body contains those lines
    
    """
    #breakpoint()
    #print(path)
    target_functions = []
    
    for func_start , func_end in function_indexes:
        
        count = 0
        patch_lines = []
        for diff in diff_lines[1:]:
            if not diff.startswith("-"):
                patch_lines.append(diff)

        flags = []
        for p in patch_lines:
            
            
            for index in range(func_start, func_end):
                if file_lines[index].strip() == p[1:].strip():
                    flags.append(True)
                    count+=1
                    break
        if len(patch_lines) == count and all(flags):
            #print(patch_lines)
            target_functions.append((func_start, func_end))


    if len(target_functions) == 1:
         start = target_functions[0][0]
         for line in file_lines[start-4:start]:
            if "(" in line:
                return line.split("(")[0]
    else:
        return None









def define_fountion_bounderies(file_lines):
    fountion_start_ends = []
    stack_boundery = []
    #breakpoint()
    for i in range(len(file_lines)):
        if "{" in file_lines[i]:
            if not len(stack_boundery):
                start = i
                
            stack_boundery.append("{")
        if "}" in file_lines[i]:
            if len(stack_boundery) == 1:
                
                end = i
                fountion_start_ends.append((start, end))
            if len(stack_boundery):
                stack_boundery.pop()
    return fountion_start_ends

def parse_patch_file(patch_file):
    files_info = {}
    with open(patch_file, 'r') as file:
        lines = file.readlines()
        file_indexes = []
        for idx in range(len(lines)):
            line = lines[idx]
            line = line.strip()
            if line.startswith('+++'):
                file_indexes.append(idx)

        jdx = 0
        while jdx < len(file_indexes):
            f_index= file_indexes[jdx]
            git_diffs = []
            start=0
            end=0
            if jdx+1 < len(file_indexes):
                start = f_index
                end = file_indexes[jdx+1]

            else:
                start = f_index
                end = len(lines)
                

            for item in lines[start:end]:
                if '@@' in item:
                    git_diffs.append(lines.index(item))

            files_info[f_index]=git_diffs
            jdx+=1

    return files_info, lines


def return_package_name(cve_ids):
    json_file = "debian_security.json"
    cve_package = {}
    cve_cwe = {}
    with open(json_file, 'r') as f:
        data = json.load(f)
        # package /CVE/
        for cve_id in tqdm(cve_ids):
            cwes = extract_all_cwe_ids(cve_id)
            cve_cwe[cve_id] = cwes
            for package in data:
                if cve_id in list(data[package].keys()):
                    cve_package[cve_id] = package
    return cve_package, cve_cwe


def extract_debug_info(binpool_path, cve, module_path):
    bins = set()
    for root, _, files in os.walk(binpool_path):
        for file in files:
            full_path = os.path.join(root, file)
            #breakpoint()
            if cve in full_path and  'vulnerable/' in full_path and 'opt0/' in full_path and 'debfiles/output_directory/bins/' in full_path:
                #breakpoint()
                if is_valid_elf(full_path):
                    # Skip non-ELF files
                    if find_corresponding_binary(full_path, module_path):
                        bins.add(full_path)
    return list(bins)
def find_corresponding_binary(binary , module_path):
    # this function checks if the binary contains the compilation unit map to module path
    with open(binary, 'rb') as file:
        elffile = ELFFile(file)
        if not elffile.has_dwarf_info():
            print('  file has no DWARF info')
            return 
        else:
            debug_info = elffile.get_dwarf_info()
            if debug_info is not None:
                for CU in debug_info.iter_CUs(): 
                    cu_die = CU.get_top_DIE()
                    
                    for att_cu in cu_die.attributes:
                        if att_cu == 'DW_AT_name':
                            cu_name = cu_die.attributes[att_cu].value.decode("utf-8")
                            if cu_name.split("/")[-1] == module_path.split("/")[-1]:
                                return True
    return False

def is_valid_elf(file_path):
    try:
        with open(file_path, 'rb') as f:
            ELFFile(f)  # Just trying to parse; if invalid, will raise exception
        return True
    except Exception:
        return False

def main():
    
    parser = argparse.ArgumentParser(description="Process path to BinPool dataset directory.")
    parser.add_argument(
        'dataset_path',
        type=str,
        help='Path to the binpool_dataset directory'
    )
    
    args = parser.parse_args()
    dataset_path = args.dataset_path
    #extract_binpool_info(dataset_path)
    #source_funcs = extract_function_names(dataset_path)
    #joblib.dump(source_funcs, "metadata/source_funcs.pkl")
    count = 0
    functions = set()
    files = set()
    source_funcs = joblib.load("metadata/source_funcs.pkl")
    cve_cwe = joblib.load("metadata/map_cwe_pack.pkl")
    cwes = []
    binpool_info = {}
    for cve in tqdm(source_funcs):
        print(cve)
        
        #print(cve_cwe[cve])
        cwes= cwes+cve_cwe[cve]
        file_func = {}
        bins = []
        for file, func in source_funcs[cve]:
            #print(file)
            if func is not None:
                #print(func)
                file_func[file] = func
                
            if file.endswith(".c") or file.endswith(".cpp"):
                
                corresponding_bins = extract_debug_info(dataset_path, cve, file)
                bins = corresponding_bins
        
        binpool_info[cve] = {'cwes': cwes, 'file_func':file_func, 'binaries':bins}

                
    with open('binpool_info.json', 'w') as f:
        json.dump(binpool_info, f, indent=4)
       

   

if __name__ == "__main__":
    main()