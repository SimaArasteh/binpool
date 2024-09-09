import argparse
import validators
import requests
import re

def find_package_page(package_name):
    debian_pack_url = "https://snapshot.debian.org/package/"
    pack_name, pack_version = package_name.split("_")
    package_page = debian_pack_url+pack_name+"/"+pack_version+"/"
    if check_url( package_page):
        return package_page
    else:
        return None


def check_url(url):
    """Check if the URL is valid."""
    if validators.url(url):
        return True
    else:
        return False

def crawl_webpage(url):
    debian_url = "https://snapshot.debian.org"
    try:
        # Fetch the content of the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Find all hrefs that end with .dsc using regular expressions
        hrefs = re.findall(r'href="([^"]+\.dsc)"', response.text)

        if len(hrefs):
            ref = hrefs[0]
            return debian_url+ref

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def create_link(input_string):
    main_url = 'https://snapshot.debian.org'
    end_substring = "pool/"
    
    # Find the position of 'pool/' in the input_string
    end_pos = input_string.find(end_substring)
    
    if end_pos != -1:
        # Extract the substring up to the position where 'pool/' starts
        extracted_string = input_string[:end_pos]
        # Concatenate the base URL with the extracted string
        final_url =  extracted_string
        return final_url
    else:
        return "The substring 'pool/' was not found in the input string."

def find_debian_release(url):
    # Extract the year from the URL using a regular expression
    input_year_match = re.search(r'\d{4}', url)
    
    if not input_year_match:
        return "No year found in URL"
    
    input_year = int(input_year_match.group(0))

    # Dictionary of Debian releases and their corresponding release years
    debian_releases = {
        "etch": 2007,
        "lenny": 2009,
        "squeeze": 2011,
        "wheezy": 2013,
        "jessie": 2015,
        "stretch": 2017,
        "buster": 2019,
        "bullseye": 2021
    }

    # Initialize the closest Debian release and the minimum difference
    closest_release = ""
    closest_diff = None

    # Iterate over the Debian releases and find the closest one to the input year
    for release, release_year in debian_releases.items():
        if release_year <= input_year:
            diff = input_year - release_year
            if closest_diff is None or diff < closest_diff:
                closest_release = release
                closest_diff = diff

    return closest_release


def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Process a package name.")
    
    # Add the package name argument
    parser.add_argument('package_name', type=str, help='Name of the package')
    
    # Parse the arguments
    args = parser.parse_args()
    
    
    pack_url_page = find_package_page(args.package_name)
    source_url = crawl_webpage(pack_url_page)
    final_url = create_link(source_url)
    debian_release = find_debian_release(final_url)
    print(debian_release)
    print(source_url)

if __name__ == "__main__":
    main()
