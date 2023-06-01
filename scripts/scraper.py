import os
import requests
from bs4 import BeautifulSoup
import json
from github import Github, InputFileContent

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

def create_directory(directory, repo):
    if not directory_exists(directory, repo):
        repo.create_file(f"{directory}/.gitkeep", "Create directory", "")

def write_json_file(file_path, data, repo):
    file_name = os.path.basename(file_path)
    directory = os.path.dirname(file_path)
    if not file_exists(file_path, repo):
        repo.create_file(f"{directory}/{file_name}", f"Create file {file_name}", json.dumps(data))

def directory_exists(directory, repo):
    try:
        repo.get_contents(directory)
        return True
    except Exception:
        return False

def file_exists(file_path, repo):
    try:
        repo.get_contents(file_path)
        return True
    except Exception:
        return False

def create_certification_folders(vendor, certifications, repo):
    vendor_dir = os.path.join("/", "it-certifications", vendor)
    create_directory(vendor_dir, repo)

    for certification, ceus in certifications.items():
        certification_dir = os.path.join(vendor_dir, certification)
        create_directory(certification_dir, repo)

        file_path = os.path.join(certification_dir, 'data.json')
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
