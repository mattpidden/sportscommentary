import requests
from bs4 import BeautifulSoup
import time

# Function to scrape and print content
def scrape_and_print(base_url, sections):
    response = requests.get(base_url)
    if response.status_code == 200:
        page_content = response.content
        soup = BeautifulSoup(page_content, 'html.parser')
        
        for section in sections:
            print(f"\n--- Scraping {section.strip('#')} Section ---")
            
            # Find the section by ID
            section_id = section.strip('#')
            section_content = soup.find(id=section_id)
            
            if section_content:
                if section_id == "LiveText":
                    # For LiveText section, match each <p> with its corresponding timestamp
                    for li in section_content.find_all('li'):
                        timestamp_span = li.find('span', {'data-testid': 'timestamp'})
                        p_tag = li.find('p')
                        
                        if timestamp_span and p_tag:
                            timestamp = timestamp_span.get_text(strip=True)
                            text = p_tag.get_text(strip=True)
                            print(f"{timestamp} - {text}")
                else:
                    # For other sections, print <p> tags on new lines
                    for p in section_content.find_all('p'):
                        print(p.get_text(strip=True))
            else:
                print(f"No content found for {section_id}")
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

def main():
    base_url = "https://www.bbc.com/sport/football/live/c8rxl24zn21t"
    sections = ['#Report', '#Scores', '#Line-ups', '#MatchStats', '#Head-to-head', '#LiveText']

    # Loop to rescrape every minute
    while True:
        scrape_and_print(base_url, sections)
        print("\nWaiting for the next scrape...\n")
        time.sleep(60)  # Wait for 1 minute before rescraping

if __name__ == "__main__":
    main()