
import os
import joblib
import re
def parse_patch_file(patch_file):
    files_info = {}
    with open(patch_file, 'r') as file:
        lines = file.readlines()
        file_indexes = []
        for idx in range(len(lines)):
            line = lines[idx]
            line = line.strip()
            if (line.startswith('+++') and line.endswith('.c')) or (line.startswith('+++') and line.endswith('.cpp')) :
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
def find_patch_lines (diff_line):
    match = re.search(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@', diff_line)
    if match:
        # Convert captured groups to integers and format them into the list as specified
        removed = [-int(match.group(1)), int(match.group(2))]
        added = [+int(match.group(3)), int(match.group(4))]
        return [removed, added]
    else:
        return None

def find_path_in_directory(directory, partial_path):
    # Walk through all directories and subdirectories
    for root, dirs, files in os.walk(directory):
        # Check if the file with the partial path exists in the current directory
        for file in files:
            # Join the root and file to create the full file path
            full_file_path = os.path.join(root, file)
            # Check if the partial path matches the end of the full path
            if full_file_path.endswith(partial_path):
                return full_file_path
    return None

def find_cfile_path (patch_path, file_name):
    # Find the position of "/debian/patches"
    #breakpoint()
    if os.path.exists(file_name):
        print("yes")
        return file_name
    path_parts = file_name.split(os.sep)
    last_two = os.path.join(path_parts[-2], path_parts[-1])
    

    index = patch_path.find("/debian/patches")

    # Extract everything before "/debian/patches"
    if index != -1:
        #extracted_path = patch_path[:index]
        extracted_path = patch_path.split("/")[0]+"/src/"
        full_path = find_path_in_directory(extracted_path, last_two)
        
        return full_path
    else:
        print("The substring '/debian/patches' was not found in the path.")

def find_function(git_diff_line):
    match = re.search(r'@@.*@@\s+[\w\s\*]+\s+(\w+)\s*\(', git_diff_line)
    if match:
        return match.group(1)
    else:
        return None
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

def extract_function_info(lis , file_info, status, path_to_patch):
    files_funcs = {}
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
            print(func_name)
            #print(changed_lines)
            target_line = None
            lines = []
            if status == "v":
                for li in diff_lines:
                    if not li.startswith('+') and '@' not in li:
                        if li.startswith('-'):
                            li = li[1:]
                        if li.strip() != '':
                            lines.append(li.strip())
            else:
                for j in diff_lines:
                    if not j.startswith('-') and '@' not in j:
                        if j.startswith('+'):
                            j = j[1:]
                        if j.strip() != '':
                            lines.append(j.strip())

            #print(path_to_patch)
            #breakpoint()
            path_for_cfile = find_cfile_path(path_to_patch, f_name)
            #print(lines)
            #print(target_line)
            #print(path_for_cfile)
            #function_name = find_function_containing_diff(path_for_cfile, lines)
            #print("here is a function name")
            #print(function_name)

            #extracted_function , extracted_line_num = explore_for_function(path_for_cfile, target_line)
            #print(extracted_function)


if __name__ == "__main__":

    '''directory ="CVE_Directories/"
    cves = set()
    cve_directories = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            cve = file_path.split("/")[1]
            cve_directories.add(directory+cve)
    print(len(cve_directories))
    joblib.dump(cve_directories, 'cve_paths.pkl')'''   
    
    '''cve_directories = joblib.load('cve_paths.pkl')
    per_cve = {}
    for director in cve_directories:
        cve = director.split("/")[1]
        per_cve[cve] = [set(), set()]
        for root, dirs, files in os.walk(director):
            for file in files:
                file_path = os.path.join(root, file)
                if 'debian/patches/' in file_path:
                    file_name = file_path.split("/")[-1]
                    patch_file = ""
                    if cve in file_name:
                        path_to_patchfile = file_path
                        per_cve[cve][0].add(path_to_patchfile)
                if '/bins/' in file_path:
                    bin_path = file_path[:file_path.index('/bins/')+6]
                    per_cve[cve][1].add(bin_path)

    joblib.dump(per_cve, 'cve_dirs.pkl')'''

    '''cve_dirs = joblib.load('cve_dirs.pkl')
    for cve in cve_dirs:
        try:
            first = list(cve_dirs[cve][0])[0]
            second = list(cve_dirs[cve][1])[0]
            status = "patch"
            patch_file_info, patch_lines = parse_patch_file(first)
            print(cve)
            extract_function_info(patch_lines, patch_file_info,status, first)
        
        except:
            print(list(cve_dirs[cve][0]))
            continue'''











            
