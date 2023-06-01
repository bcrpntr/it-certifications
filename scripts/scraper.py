import os
import requests
from bs4 import BeautifulSoup
import json
from github import Github

urls = {
    'https://www.comptia.org/continuing-education/choose/renewing-with-multiple-activities/additional-comptia-certifications': 'CompTIA'
}

def scrape_comptia(url):
    r = requests.get(url)
    r.raise_for_status()

    soup = BeautifulSoup(r.content, 'html.parser')

    accordion = soup.find(id='accordion3')
    items = accordion.find_all(class_='accordion-item')

    data = {}
    for item in items:
        certification_element = item.find(class_='title')
        ceus_element = item.find('strong')

        if certification_element and ceus_element:
            certification = certification_element.get_text(strip=True)
            ceus_granted = ceus_element.next_sibling.strip() if ceus_element.next_sibling else 'N/A'
            data[certification] = ceus_granted

    return data

def write_json_file(file_path, data, repo):
    file_name = os.path.basename(file_path)
    directory = os.path.dirname(file_path)
    try:
        repo.get_contents(file_path)
    except:
        repo.create_file(f"{directory}/{file_name}", f"Create file {file_name}", json.dumps(data))

def create_certification_folders(vendor, certifications, repo):
    for certification, ceus in certifications.items():
        if ceus == 'N/A':
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
