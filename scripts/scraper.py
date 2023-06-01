import os
import requests
from bs4 import BeautifulSoup
import json

urls = {
    'https://www.comptia.org/continuing-education/choose/renewing-with-multiple-activities/additional-comptia-certifications': 'CompTIA'
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
            ceus_granted = ceus_element.next_sibling.strip() if ceus_element and ceus_element.next_sibling else 'N/A'
            data[certification] = ceus_granted

    return data

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def write_json_file(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f)

def create_certification_folders(vendor, certifications):
    vendor_dir = os.path.join(os.getcwd(), vendor)
    create_directory(vendor_dir)

    for certification, ceus in certifications.items():
        certification_dir = os.path.join(vendor_dir, certification)
        create_directory(certification_dir)

        file_path = os.path.join(certification_dir, 'data.json')
        write_json_file(file_path, {certification: ceus})

def main():
    for url, vendor in urls.items():
        data = scrape_comptia(url)
        create_certification_folders(vendor, data)

if __name__ == '__main__':
    main()
