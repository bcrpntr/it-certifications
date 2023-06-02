import os
import requests
from bs4 import BeautifulSoup
import json
from github import Github
import re

urls = {
    'https://www.comptia.org/continuing-education/choose/renewing-with-multiple-activities/additional-comptia-certifications': 'CompTIA'
}

import re  # Add this import at the top of your script

def scrape_comptia(url):
    r = requests.get(url)
    r.raise_for_status()

    soup = BeautifulSoup(r.content, 'html.parser')

    accordion = soup.find(id='accordion3')
    items = accordion.find_all(class_='accordion-item')

    data = {}
    for item in items:
        certification_element = item.find(class_='title')
        ceus_element = item.find('p')  # Fetch the 'p' tag content first

        if certification_element and ceus_element:
            certifications = certification_element.get_text(strip=True).split(',')
            
            # Splitting on '–' since this is the character between required certification and CEUs granted
            content_parts = ceus_element.get_text(strip=True).split('–', 1)

            required_certification = content_parts[0].strip() if len(content_parts) > 1 else "N/A"

            # Within 'p' tag content, fetch 'strong' tag for CEUs
            ceus_content = ceus_element.find('strong').get_text(strip=True) if ceus_element.find('strong') else 'N/A'

            # Extract only the numeric part of ceus_content if "CEUs" present in the string
            ceus_granted_search = re.search(r'(\d+)\s*CEUs?', ceus_content, re.IGNORECASE)
            ceus_granted = ceus_granted_search.group(1) if ceus_granted_search else 'N/A'

            for certification in certifications:
                certification = certification.strip()  # Remove leading and trailing whitespace

                # Ensure ceus_granted is not 'N/A' or an empty string, and is a digit
                if ceus_granted not in {'N/A', ''} and ceus_granted.isdigit():
                    data[certification] = {
                        "Required Certification": required_certification,
                        "CEUs Granted": ceus_granted
                    }
    return data

def write_json_file(file_path, data, repo):
    file_name = os.path.basename(file_path)
    directory = os.path.dirname(file_path)
    try:
        repo.get_contents(file_path)
    except:
        repo.create_file(f"{directory}/{file_name}", f"Create file {file_name}", json.dumps(data, indent=4))

def create_certification_folders(vendor, certifications, repo):
    for certification, ceus in certifications.items():
        if ceus == 'N/A' or ceus == '':
            continue
        file_path = os.path.join(vendor, certification, 'data.json')
        write_json_file(file_path, {certification: ceus}, repo)

def main():
    github_token = os.getenv('TOKEN')
    g = Github(github_token)
    repo = g.get_repo("bcrpntr/it-certifications")

    for url, vendor in urls.items():
        data = scrape_comptia(url)
        create_certification_folders(vendor, data, repo)

if __name__ == '__main__':
    main()
