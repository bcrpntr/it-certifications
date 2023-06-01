import os
import requests
from bs4 import BeautifulSoup
import json

urls = {
    'https://www.comptia.org/continuing-education/choose/renewing-with-multiple-activities/additional-comptia-certifications': ('comptia', 'additional-comptia-certifications')
}

def scrape_comptia(url):
    # Send a request to the website
    r = requests.get(url)
    r.raise_for_status()

    # Parse the HTML content
    soup = BeautifulSoup(r.content, 'html.parser')

    # Find the relevant elements based on the HTML structure
    accordion = soup.find(id='accordion3')
    items = accordion.find_all(class_='accordion-item')

    # Extract the certifications and CEUs granted
    data = {}
    for item in items:
        certification_element = item.find(class_='title')
        ceus_element = item.find('strong')

        if certification_element:
            certification = certification_element.get_text(strip=True)

            if ceus_element:
                if ceus_element.find_next_sibling('p'):
                    ceus_granted = ceus_element.find_next_sibling('p').get_text(strip=True)
                else:
                    ceus_granted = 'N/A'
            else:
                ceus_granted = 'N/A'

            data[certification] = ceus_granted

    return data

def create_directory(vendor, certification):
    # Create a directory for the vendor if it doesn't exist
    if not os.path.exists(vendor):
        os.makedirs(vendor)

    # Create a directory for the certification if it doesn't exist
    certification_dir = os.path.join(vendor, certification)
    if not os.path.exists(certification_dir):
        os.makedirs(certification_dir)

    return certification_dir

scraping_functions = {
    'comptia': scrape_comptia
}

data = {}
for url, (vendor, certification) in urls.items():
    scraping_function = scraping_functions.get(vendor)
    if scraping_function:
        data[url] = scraping_function(url)
        for cert, ceus in data[url].items():
            certification_dir = create_directory(vendor, cert)
            file_path = os.path.join(certification_dir, 'data.json')
            with open(file_path, 'w') as f:
                json.dump({cert: ceus}, f)

# Write to a json file
with open('data.json', 'w') as f:
    json.dump(data, f)
