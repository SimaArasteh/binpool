import json
import argparse
import os 
import re
import joblib
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

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

    print(len(set(list_cwes)))

    joblib.dump(list_deb_files, "metadata/list_deb_files.pkl")
    joblib.dump(list_cves, "metadata/list_cves.pkl")
    joblib.dump(map_cve_pack, "metadata/map_cve_pack.pkl")
    joblib.dump(map_cve_cwe, "metadata/map_cwe_pack.pkl")

def extract_function_names(dataset_path):

    for root, dirs, files in os.walk(dataset_path):
        for filename in files:
            full_path = os.path.join(root, filename)
            if full_path.endswith(".patch") and 'opt0' in full_path:
                file_infos, file_lines = parse_patch_file(full_path)
                extract_function_info(file_lines, file_infos, 's', full_path)
                #print(file_infos)

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
    match = re.search(r'@@.*@@\s+[\w\s\*]+\s+(\w+)\s*\(', git_diff_line)
    if match:
        return match.group(1)
    else:
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
    for file_idx in file_info:
        file_name = lis[file_idx]
        f_name = file_name.split(" ")[-1].strip()
        git_lines = file_info[file_idx]
        modifided_lines = find_lines_for_diff(lis, git_lines)
        for l in git_lines:
            git_line = lis[l]
            git_line = git_line.strip()
            diff_lines = modifided_lines[l]
            func_name = find_function(git_line)
            changed_lines = find_patch_lines(git_line)
            #print(func_name)
            #print(changed_lines)
            target_line = None


           
            if func_name is not None:
                print(func_name)
                funcs.add( func_name)
            #extracted_function , extracted_line_num = explore_for_function(path_for_cfile, target_line)
            #print(extracted_function)

    return funcs

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
    extract_function_names(dataset_path)
    

   

if __name__ == "__main__":
    main()