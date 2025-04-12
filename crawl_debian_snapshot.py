import requests
from bs4 import BeautifulSoup
import joblib
from tqdm import tqdm
from collections import defaultdict
import random
import time
import subprocess
def extract_url_packages():
    # URL of the web page
    url = "https://snapshot.debian.org/"  # Replace with your actual URL
    urls = []
    # Send a GET request to fetch the page content
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the <ul> with class "inlineList"
        ul_element = soup.find('ul', class_='inlineList')
        
        if ul_element:
            # Extract all href attributes from <a> tags inside <li>
            hrefs = [a['href'] for a in ul_element.find_all('a')]
            main_url = "https://snapshot.debian.org/"
            for href in hrefs: 
                url = main_url+href
                urls.append(url)
            #joblib.dump(urls, "url_to_all_packages.pkl")
            # Print the results
            #print("Extracted hrefs:", hrefs)
        else:
            print("No <ul> with class 'inlineList' found on the page.")
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")

def extract_url_package_alphabet(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the <p> tag
        p_tag = soup.find('p')
        if p_tag:
            # Extract href attributes from all <a> tags inside the <p>
            hrefs = [a['href'] for a in p_tag.find_all('a', href=True)]
            return hrefs
        else:
            return []  # No <p> tag found
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

def crawl_available_versions(url):
    try:
        # Send a GET request to the webpage
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP request errors
        
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the <p> tag containing "Available versions:"
        p_tag = soup.find('p', string=lambda text: text and "Available versions:" in text)
        
        if p_tag:
            # Find the <ul> tag immediately after the <p> tag
            ul_tag = p_tag.find_next('ul')
            
            if ul_tag:
                # Extract all href attributes from <a> tags inside the <ul>
                hrefs = [a['href'] for a in ul_tag.find_all('a', href=True)]
                return hrefs
            else:
                print("No <ul> tag found after the <p> tag.")
                return []
        else:
            print("No <p> tag with 'Available versions:' found.")
            return []
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []

def crawl_webpage(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            hrefs = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.tar.xz')]
            return hrefs
        return []
    except requests.RequestException:
        return []

def download_file_with_wget(url, save_path):
    try:
        # Use the wget command to download the file
        subprocess.run(['wget', '-P', save_path, url], check=True)
        print(f"File downloaded successfully and saved to: {save_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading file: {e}")
    except FileNotFoundError:
        print("wget command not found. Make sure wget is installed.")

if __name__ == "__main__":
    '''urls = joblib.load("url_to_all_packages.pkl")
    main_url = "https://snapshot.debian.org/package/"
    url_all_packages = []
    for url in tqdm(urls):
        hrefs_url = extract_url_package_alphabet(url)
        for item in hrefs_url:
            final_url = main_url+item
            url_all_packages.append(final_url)
    joblib.dump(url_all_packages, 'url_all_packages.pkl')'''
    '''url_all_packages = joblib.load('url_all_packages.pkl')
    package_versions_url = defaultdict(list)
    for package in tqdm(url_all_packages):
        time.sleep(random.uniform(1, 3))
        refs = crawl_available_versions(package)
        #print(package)
        for ref in refs:
            final_ref = package+ref
            #print(final_ref)
            package_versions_url[package].append(package+ref)
    
    joblib.dump(package_versions_url, 'package_versions_url.pkl')'''
    package_versions_url = joblib.load('package_versions_url.pkl')
    save_path = "debianpack_debiantar/"
    keys = list(package_versions_url.keys())
    #breakpoint()
    start = "https://snapshot.debian.org/package/cppcheck/"
    start_index = keys.index(start) if start in keys else 0
    for key in tqdm(keys[start_index+1:]):
        #print(pack.split("/")[-2])
        
        for item in package_versions_url[key]:
            time.sleep(2)
            hrefs = crawl_webpage(item)
            if len(hrefs):
                url_debiantar = 'https://snapshot.debian.org/'+hrefs[0]
                time.sleep(2)
                download_file_with_wget(url_debiantar, save_path)

             
        





    

