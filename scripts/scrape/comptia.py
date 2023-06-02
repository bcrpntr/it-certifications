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
