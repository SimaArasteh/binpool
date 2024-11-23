import clang.cindex

def find_function_boundaries(file_path):
    """
    Parses a C/C++ file and identifies function boundaries using a stack.
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        function_boundaries = []
        stack = []
        function_start = None
        line_number = 0

        for line in lines:
            line_number += 1
            stripped_line = line.strip()

            # Check for opening braces
            if "{" in stripped_line:
                stack.append(line_number)
                # If stack was empty, this is the start of a new block
                if len(stack) == 1:
                    function_start = line_number

            # Check for closing braces
            if "}" in stripped_line:
                if stack:
                    stack.pop()
                # If stack is empty, we've closed a function
                if not stack and function_start is not None:
                    function_boundaries.append((function_start, line_number))
                    function_start = None

        # Print results
        if function_boundaries:
            print(f"Functions detected in '{file_path}':")
            for start, end in function_boundaries:
                #print(f"Function from line {lines[start-2]} to {end}")
                code_str = "".join(l for l in lines[start-2:start])
                print(code_str)
                res = classify_names_by_kind(code_str)
                print(res)
                print("***********")
        else:
            print(f"No functions detected in '{file_path}'.")

        return function_boundaries

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example Usage


def classify_names_by_kind(code: str):
    """
    Analyzes a piece of C/C++ code using Clang and classifies names as functions, variables, etc.
    
    Args:
        code (str): A string containing C/C++ code.

    Returns:
        list: A list of dictionaries with name, kind (e.g., function, variable), and location.
    """
    # Temporary file to store code for parsing
    temp_file = "temp_code.cpp"
    
    # Write the code to the temporary file
    with open(temp_file, "w") as file:
        file.write(code)

    # Initialize Clang index
    index = clang.cindex.Index.create()
    
    # Parse the code with Clang
    translation_unit = index.parse(temp_file, args=['-std=c++17'])

    # List to store results
    result = []

    # Recursive function to explore nodes in the AST
    def explore_ast(node):
        # Extract relevant kinds
        if node.kind in [
            clang.cindex.CursorKind.FUNCTION_DECL,
            clang.cindex.CursorKind.VAR_DECL,
            clang.cindex.CursorKind.PARM_DECL,
            clang.cindex.CursorKind.FIELD_DECL,
        ]:
            name = node.spelling or node.displayname
            kind = node.kind.name
            location = f"{node.location.file}:{node.location.line}" if node.location.file else "Unknown"
            result.append({
                "name": name,
                "kind": kind,
                "location": location,
            })

        # Recurse into child nodes
        for child in node.get_children():
            explore_ast(child)

    # Start exploring from the root node
    explore_ast(translation_unit.cursor)

    return result
if __name__ == "__main__":
    file_path = "CVE_Directories/CVE-2018-20349/r-cran-igraph-1.2.4.1/.pc/CVE-2018-20349.patch/src/foreign-graphml.c"  # Replace with your C/C++ file path
    bounderies = find_function_boundaries(file_path)
