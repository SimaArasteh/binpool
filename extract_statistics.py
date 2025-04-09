import json
import argparse
import os 
import re
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
    extract_binpool_info(dataset_path)
    

   

if __name__ == "__main__":
    main()