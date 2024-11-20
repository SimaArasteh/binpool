
import os
import joblib
import re
import clang.cindex
from clang import cindex
import tempfile
index = clang.cindex.Index.create()
def parse_patch_file(patch_file):
    files_info = {}
    with open(patch_file, 'r') as file:
        lines = file.readlines()
        file_indexes = []
        for idx in range(len(lines)):
            line = lines[idx]
            line = line.strip()
            if (line.startswith('+++') and line.endswith('.c')) or (line.startswith('+++') and line.endswith('.cpp')) or (line.startswith('+++') and line.endswith('.go'))  or (line.startswith('+++') and line.endswith('.py'))  or (line.startswith('+++') and line.endswith('.java')) :
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
    print(partial_path)
    # Walk through all directories and subdirectories
    for root, dirs, files in os.walk(directory):
        # Check if the file with the partial path exists in the current directory
        for file in files:
            # Join the root and file to create the full file path
            full_file_path = os.path.join(root, file)
            # Check if the partial path matches the end of the full path
            if full_file_path.endswith(partial_path) and '/.pc/' in full_file_path:
                return full_file_path
    return None

def find_cfile_path (patch_path, file_name):
    # Find the position of "/debian/patches"
    #breakpoint()

    
    path_parts = file_name.split(os.sep)
    if path_parts[0] == "b" or path_parts[0] == "a":
        path_parts = path_parts[1:]
    if len(path_parts) > 1:
        last_two = os.path.join(path_parts[-2], path_parts[-1])
    elif len(path_parts) == 1:
        last_two = path_parts[0]

    indexp = patch_path.find("/debian/patches")

    # Extract everything before "/debian/patches"
    if indexp != -1:
        ps = patch_path.split("/")
        extracted_path = os.path.join(ps[0], ps[1])
        #extracted_path = patch_path.split("/")[0]+"/src/"
        full_path = find_path_in_directory(extracted_path, last_two)
        
        return full_path
    else:
        print("The substring '/debian/patches' was not found in the path.")

def extract_func_name(git_line):
    if "(" in git_line:
        return git_line.split("(")[0].split(" ")[-1]
    return None



def extract_function_name_with_clang(code_line: str) -> str:
    """
    Extracts the function name from a single line of C code using Clang.

    Args:
        code_line (str): A line of C code.

    Returns:
        str: The extracted function name, or None if not found.
    """
    # Create a temporary file with a basic wrapper for the line

    with tempfile.NamedTemporaryFile(suffix=".c", delete=False) as temp_file:
        temp_file.write(code_line.encode('utf-8'))
        temp_file_name = temp_file.name

    # Initialize the Clang index
    index = clang.cindex.Index.create()

    # Parse the temporary file
    translation_unit = index.parse(temp_file_name)

    # Search for the function declaration
    for node in translation_unit.cursor.walk_preorder():
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            # Return the function name
            return node.spelling

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

def find_function_containing_diff(filepath, diff_lines):
    """Find which function contains all the lines from the diff."""
    #breakpoint()
    functions = get_function_code_and_ranges(filepath)
    
    for func_name, body_start, body_end, function_code in functions:
        
        if match_diff_lines_with_function(function_code, diff_lines):
            return func_name
    return None

def get_function_code_and_ranges(filepath):
    """Parse the C/C++ file and return a list of functions with their code content and start/end line numbers."""
    #breakpoint()
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
    '''for func in functions:
        if func[0] == "opj_j2k_write_mco":
            print("this is me")
            print((func[1], func[2]))'''
    return functions
    
def match_diff_lines_with_function(function_code, diff_lines):
    """Check if all diff lines are contained within the function's body."""
    #breakpoint()
    function_code_str = ''.join([line.strip() for line in function_code])
    #diff_lines_str = ''.join([line.strip() for line in diff_lines])
    count = 0
    for l in diff_lines:
        #if l != '':
        if l in function_code_str:
            count+=1
        

    if count / len(diff_lines) > 0.5:
        return True
    else:
        return False

    
def extract_function_info(lis , file_info, status, path_to_patch):
    #breakpoint()
    files_funcs = {}
    unique_funcs = set()
    for file_idx in file_info:
        file_name = lis[file_idx]
        f_name = file_name.split(" ")[-1].strip()
        git_lines = file_info[file_idx]
        modifided_lines = find_lines_for_diff(lis, git_lines)
        for l in git_lines:
            git_line = lis[l]
            git_line = git_line.strip()
            diff_lines = modifided_lines[l]
            func_name = extract_func_name(git_line)
            changed_lines = find_patch_lines(git_line)
            #print(git_line)
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

            
            #breakpoint()
            print(git_line)
            if func_name is not None:
                if func_name != "":
                    unique_funcs.add(func_name)
                print(func_name)
            else:

                path_for_cfile = find_cfile_path(path_to_patch, f_name)
                print("file_name")
                print(f_name)
                print(path_to_patch)
                print(path_for_cfile)
                #print(lines) 
                #print(target_line)
                #print(path_for_cfile)
               
                function_name = find_function_containing_diff(path_for_cfile, lines)
                print("here is a function name")
                print(function_name)
                if function_name is not None:
                    unique_funcs.add(function_name)

    return unique_funcs

def contains_specific_cve(file_path, cve_id):
    """
    Reads a file and checks if it contains a specific CVE ID.
    
    Args:
        file_path (str): Path to the file.
        cve_id (str): The specific CVE ID to search for (e.g., 'CVE-2023-12345').
    
    Returns:
        bool: True if the CVE ID is found, False otherwise.
    """
    try:
        # Open and read the file
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Check if the specific CVE ID is in the file
        if cve_id in content:
            return True
        else:
            return False
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

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
    #breakpoint()
    for director in cve_directories:
        
        cve = director.split("/")[1]
        #print(cve)
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
                    elif contains_specific_cve(file_path, cve) and file_name!='series':
                        per_cve[cve][0].add(file_path)




                if '/bins/' in file_path:
                    bin_path = file_path[:file_path.index('/bins/')+6]
                    per_cve[cve][1].add(bin_path)
        if not len(per_cve[cve][0]):
            print(cve)
    joblib.dump(per_cve, 'cve_dirs.pkl')'''

    cve_dirs = joblib.load('cve_dirs.pkl')
    count = 0

    list_funcs = []
    for cve in cve_dirs:
        #if cve == 'CVE-2019-12110':
        try:
            #print(cve)
            #breakpoint()
            first = list(cve_dirs[cve][0])[0]
            #second = list(cve_dirs[cve][1])[0]
            status = "patch"
            patch_file_info, patch_lines = parse_patch_file(first)
            print(cve)
            funcs = extract_function_info(patch_lines, patch_file_info,status, first)
            print("**************")
            list_funcs += list(funcs)
            
        except:
            continue 
    print(len(cve_dirs.keys()))       
    print(len(list_funcs))
    
    








            
