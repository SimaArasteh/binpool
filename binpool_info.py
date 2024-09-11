
# We 
import argparse
import os
import sys
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

def extract_function_info(lis , file_info):
    files_funcs = {}
    for file_idx in file_info:
        file_name = lis[file_idx]
        f_name = file_name.split(" ")[-1].strip()
        git_lines = file_info[file_idx]
        
        for l in git_lines:
            git_line = lis[l]
            git_line = git_line.strip()
            func_name = find_function(git_line)
            changed_lines = find_patch_lines(git_line)
            print(func_name)
            print(changed_lines)


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

def explore_for_function(file_name,code_line):



def main():
    
    parser = argparse.ArgumentParser(description="Process binary directory and patch file paths.")
    parser.add_argument('-b', '--binaries_dir', required=True, type=str, help='Path to the directory containing the binaries')
    parser.add_argument('-p', '--patch_file', required=True, type=str, help='Path to the patch file')
    
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
    extract_function_info(patch_lines, patch_file_info)




if __name__ == "__main__":
    main()
