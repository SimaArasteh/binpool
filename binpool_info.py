
# We 
import argparse
import os
import sys
import re
import clang.cindex
from clang import cindex
import os
import json
#clang.cindex.Config.set_library_file('/mnt/debian11/usr/lib/llvm-11/lib/libclang.so.1')
index = clang.cindex.Index.create()
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
            if func_name is None:
                target_dir = '/'.join(path_to_patch.split("/")[:5])
                #print(target_dir)
                path_for_cfile = find_cfile_path_for_patch(target_dir)
                print(path_for_cfile)
                #function_name = find_function_containing_diff(path_for_cfile, lines)
                #print("here is a function name")
                #print(function_name)

            #path_for_cfile = find_cfile_path(path_to_patch, f_name)
            #print(lines)
            #print(target_line)
            #print(path_for_cfile)
            #function_name = find_function_containing_diff(path_for_cfile, lines)
            #print("here is a function name")
            #print(function_name)
            if func_name is not None:
                funcs.add( func_name)
            #extracted_function , extracted_line_num = explore_for_function(path_for_cfile, target_line)
            #print(extracted_function)

    return funcs

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


def find_cfile_path_for_patch(cve_directory):
    cve = cve_directory.split("/")[-1]

    for root, directories, files in os.walk(cve_directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            patch_name = filepath.split("/")[-2]
            if '.pc' in filepath and cve in patch_name:
                return filepath
                





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

def get_function_code_and_ranges(filepath):
    """Parse the C/C++ file and return a list of functions with their code content and start/end line numbers."""
    translation_unit = index.parse(filepath)
    functions = []

    def extract_function_code(node):
        # If the node is a function, get the name and code content
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            # Clang gives us the function declaration, but we want the body (between { and })
            start_line = node.extent.start.line
            body_start = None
            body_end = None

            # Find the first occurrence of the function body
            for child in node.get_children():
                if child.kind == clang.cindex.CursorKind.COMPOUND_STMT:
                    #breakpoint()
                    body_start = child.extent.start.line
                    body_end = child.extent.end.line
                    break

            if body_start and body_end:
                # Extract the code for the function's body (from body_start to body_end)
                with open(filepath, 'r') as file:
                    code_lines = file.readlines()[body_start - 1:body_end]

                functions.append((node.spelling, body_start, body_end, code_lines))

        # Recurse through the children of the node
        for child in node.get_children():
            extract_function_code(child)

    # Start from the root node (translation unit)
    extract_function_code(translation_unit.cursor)
    for func in functions:
        if func[0] == "opj_j2k_write_mco":
            print("this is me")
            print((func[1], func[2]))
    return functions

def match_diff_lines_with_function(function_code, diff_lines):
    """Check if all diff lines are contained within the function's body."""
    #breakpoint()
    function_code_str = ''.join([line.strip() for line in function_code])
    #diff_lines_str = ''.join([line.strip() for line in diff_lines])
    flag = True
    for l in diff_lines:
        #if l != '':
        if l in function_code_str:
            continue
        else:
            flag = False

    return flag
    


def find_function_containing_diff(filepath, diff_lines):
    """Find which function contains all the lines from the diff."""
    functions = get_function_code_and_ranges(filepath)
    
    for func_name, body_start, body_end, function_code in functions:
        
        if match_diff_lines_with_function(function_code, diff_lines):
            return func_name
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

def explore_for_function(file_path,target_line):
    # Sometimes function names does not apear in the git diff line
    # In this case, we read the C file and look for the lines and 
    # check which function these lines belong to
    # It is also good to check the changed lines because sometimes
    # after removing the patch using quilt, lines do not
    # match with the lines in the git diff
    #breakpoint()
    # Regular expression to match a function declaration/definition
    function_pattern = re.compile(r'^\s*(\w[\w\s*&<>]*)\s+(\w+)\s*\(([^)]*)\)\s*\{')
    
    function_stack = []
    current_function = None
    inside_function = False
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            # Check for function start
            match = function_pattern.match(line)
            if match:
                # Found a function definition, store the name
                function_name = match.group(2)
                function_stack.append(function_name)
                current_function = function_name
                inside_function = True
            
            # Check if we found the target line
            if line.strip() == target_line.strip() and inside_function:
                return current_function, lines.index(line)
            
            # Check for function end by counting closing braces
            if '}' in line and inside_function:
                if function_stack:
                    function_stack.pop()
                    if not function_stack:
                        inside_function = False
                        current_function = None
                    else:
                        current_function = function_stack[-1]

    # If no function is found for the line
    return None

def parse_json_debian_security(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
        print(data)

def main():
    
    directory = "/workspaces/binpool/binpool_final_release/"
    cves = set()
    all_functions = []
    count = 0
    for root, dirs, files in os.walk(directory):
        for filename in files:
            path_file = os.path.join(root, filename)
            path_name = path_file.split("/")[-1]
            cve_target2 = path_file.split("/")[4]
            if path_file.endswith(".patch") and '_opt' in path_name:
                #print(path_file)
                patch_file_info, patch_lines = parse_patch_file(path_file)
    
                functions = extract_function_info(patch_lines, patch_file_info, 'p', path_file)
                #print(functions)
                if len(functions):
                    cves.add(cve_target2)
                all_functions = all_functions+list(functions)
                
            else:
                if 'debian/patches/' in  path_file and path_file.endswith(".patch"):
                    path_name = path_file.split("/")[-1]
                    cve_pattern = r'CVE-\d{4}-\d{4,}'
                    cve_list = re.findall(cve_pattern, path_name)
                    cve_target = path_file.split("/")[4]
                    
                    with open(path_file, 'r') as file:
                        lines = file.read()
                    for cve in cve_list:
                        if cve == cve_target or cve in lines:
                            patch_file_info, patch_lines = parse_patch_file(path_file)
    
                            functions = extract_function_info(patch_lines, patch_file_info, 'p', path_file)
                            if len(functions):
                                cves.add(cve_target2)
                            all_functions = all_functions+list(functions)
                            
                            
    print(len(set(cves)))
    print(len(set(all_functions)))             
    

    '''parser = argparse.ArgumentParser(description="Process binary directory and patch file paths.")
    parser.add_argument('-b', '--binaries_dir', required=True, type=str, help='Path to the directory containing the binaries')
    parser.add_argument('-p', '--patch_file', required=True, type=str, help='Path to the patch file')
    parser.add_argument('-s', '--status', required=True, type=str, help='define if the built package is patched or vulnerable')
    args = parser.parse_args()

    # Check if the binaries directory exists
    if not os.path.isdir(args.binaries_dir):
        print(f"Error: The directory '{args.binaries_dir}' does not exist.")
        sys.exit(1)
    
    # Check if the patch file exists
    if not os.path.isfile(args.patch_file):
        print(f"Error: The patch file '{args.patch_file}' does not exist.")
        sys.exit(1)
    

    patch_file_info, patch_lines = parse_patch_file(args.patch_file)
    
    extract_function_info(patch_lines, patch_file_info, args.status, args.patch_file)'''




if __name__ == "__main__":
    main()
