import argparse
import requests
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import joblib
from tqdm import tqdm
# Function to create a Debian snapshot URL
def create_debian_url(param_value):
    delimiter = "_"

    # Find the position of the first occurrence of the delimiter
    position = param_value.find(delimiter)

    # Extract the substrings before and after the delimiter
    substring1 = param_value[:position]
    substring2 = param_value[position + 1:]

    # Construct the URL
    url = 'https://snapshot.debian.org/package'
    final_url = f"{url}/{substring1}/{substring2}"
    return final_url

# Function to check if the URL is valid
def check_valid_url(url):
    try:
        response = requests.head(url)
        if response.status_code == 200:
            return True
        return False
    except requests.RequestException:
        return False

# Function to crawl the webpage and find hrefs that end with ".dsc"
def crawl_webpage(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            hrefs = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.dsc')]
            return hrefs
        return []
    except requests.RequestException:
        return []

# Main function
def url_source(tuples_second_index_value):
    # Step 1: Create the Debian URL
    result = create_debian_url(tuples_second_index_value)
    #print(f"Processed result: {result}")
    
    #wait_time = 2
    #sleep(wait_time)

    # Step 2: Check if the URL is valid
    is_valid = check_valid_url(result+"/")
    #print(f"Is URL valid: {is_valid}")

    # Step 3: If the URL is valid, crawl the webpage
    if is_valid:
        #sleep(wait_time)
        links = crawl_webpage(result)

        # Step 4: Check for '/debian/' in href and build the full source URL
        main_url = 'https://snapshot.debian.org'
        for href in links:
            if '/debian/' in href:
                source_url = f"{main_url}{href}"
                return source_url
                #print(f"Found source URL: {source_url}")

if __name__ == "__main__":
    #parser = argparse.ArgumentParser(description="Process Debian URLs and crawl web pages")
    #parser.add_argument('tuples_second', type=str, help="The second tuple value to process")

    #args = parser.parse_args()
    #main(args.tuples_second)
    df = pd.read_csv('binpool2.csv')
    second_column = df.iloc[:, 1].tolist()
    list_links = []
    for item in tqdm(second_column):
        src = url_source(item)
        print(src)
        list_links.append((item,src ))

    joblib.dump(list_links, 'binpool_src_links.pkl')
  