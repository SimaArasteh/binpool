import argparse




def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Process a package name.")
    
    # Add the package name argument
    parser.add_argument('package_name', type=str, help='Name of the package')
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Use the package name (this is a placeholder for your logic)
    print(f"Package name provided: {args.package_name}")

if __name__ == "__main__":
    main()
