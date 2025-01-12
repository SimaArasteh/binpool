import json
import joblib
import pandas as pd

file_path = "debiansecurity.json"
df = pd.read_csv('binpool.csv')
list_cves = list(set(df['cve'].tolist()))
print(list_cves)
# package - CVE- 'releases' - release-names- fixed version
data_sheets = []
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)
    #print(data['389-ds-base']['CVE-2012-0833']['releases']['bookworm']['fixed_version'])
    for pack_name in data:
        for cve in data[pack_name]:
            
            for r in data[pack_name][cve]['releases']:
                #print(r)
                if 'fixed_version' in data[pack_name][cve]['releases'][r].keys():
                    fix = data[pack_name][cve]['releases'][r]['fixed_version']
                    #print(pack_name+"_"+fix)
                    if fix != '0':
                        data_sheets.append((cve, pack_name+"_"+fix))


columns = ["cve", "fix_version"]

df = pd.DataFrame(list(set(data_sheets)), columns=columns)

file_name = "binpool2.csv"
df.to_csv(file_name, index=False)