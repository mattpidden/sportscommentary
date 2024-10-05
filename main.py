import requests
from bs4 import BeautifulSoup
import time
import io
import pyttsx3

# Load a pre-trained text generation model
#generator = pipeline('text-generation', model='gpt2')  # You can choose a different model if needed

# Function to scrape Live Text section
def scrape_live_text(soup):
    live_text = []
    live_text_section = soup.find(id='LiveText')
    if live_text_section:
        for li in live_text_section.find_all('li'):
            timestamp_span = li.find('span', {'data-testid': 'accessible-timestamp'})
            p_tag = li.find('p')
            
            if timestamp_span and p_tag:
                timestamp = timestamp_span.get_text(strip=True)
                text = p_tag.get_text(strip=True)
                live_text.append(f"{timestamp} - {text}")
    return live_text

# Function to scrape Match Report section
def scrape_match_report(soup):
    report_section = soup.find(id='Report')
    if report_section:
        for p in report_section.find_all('p'):
            print(p.get_text(strip=True))

# Function to scrape Scores section
def scrape_scores(soup):
    scores_section = soup.find(id='Scores')
    if scores_section:
        for p in scores_section.find_all('p'):
            print(p.get_text(strip=True))

# Function to scrape Line-ups section
def scrape_lineups(soup):
    lineups_section = soup.find(id='Line-ups')
    if lineups_section:
        for p in lineups_section.find_all('p'):
            print(p.get_text(strip=True))

# Function to scrape Match Stats section
def scrape_match_stats(soup):
    match_stats_section = soup.find(id='MatchStats')
    if match_stats_section:
        for p in match_stats_section.find_all('p'):
            print(p.get_text(strip=True))

# Function to scrape Head-to-Head section
def scrape_head_to_head(soup):
    head_to_head_section = soup.find(id='Head-to-head')
    if head_to_head_section:
        for p in head_to_head_section.find_all('p'):
            print(p.get_text(strip=True))

# Function to fetch and parse the webpage
def fetch_and_parse(base_url):
    response = requests.get(base_url)
    if response.status_code == 200:
        page_content = response.content
        soup = BeautifulSoup(page_content, 'html.parser')
        return soup
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None

def speak_text(text):
    engine = pyttsx3.init()

    # Adjust speech rate (default is around 200, lower it to make it slower)
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 40)

    # Change voice (you can change the index for different voices)
    #//voices = engine.getProperty('voices')
    #engine.setProperty('voice', voices[0].id)  # Try voices[1] or others for different pitch

    engine.say(text)
    engine.runAndWait()


def generate_commentary(live_text):
    #prompt = f"Convert the following live text into sports commentary from a pundit: {live_text}"
    #response = generator(prompt, max_length=100, num_return_sequences=1)
    #commentary = response[0]['generated_text']
    return live_text

# Main function to scrape and print content
def main():
    base_url = "https://www.bbc.co.uk/sport/football/live/czj9v2dpd11t"
    
    processed_entries = set()  # Store processed entries here
    
    # Loop to rescrape every minute
    while True:
        print("\n--- Starting new scrape cycle ---")
        
        soup = fetch_and_parse(base_url)
        
        if soup:
            print("Soup successfully fetched.")
            live_text = scrape_live_text(soup)
            print(f"Live text entries scraped: {len(live_text)}")

            # Filter out entries that have already been processed
            new_entries = [entry for entry in live_text if entry not in processed_entries]
            print(f"New entries to process: {len(new_entries)}")

            if new_entries:
                for entry in new_entries[::-1]:  # Reverse to process newest first
                    print(f"Processing new live text entry: {entry}")
                    speak_text(entry)

                # Add new entries to the processed set
                processed_entries.update(new_entries)
                print(f"Processed entries updated. Total processed: {len(processed_entries)}")
            else:
                print("No new entries found.")
        else:
            print("Failed to fetch the page content.")
        
        print("\nWaiting for the next scrape...\n")
        time.sleep(5)  # Wait for 5 seconds before rescraping (use 30 seconds for live runs)


            

            #print("\n--- Scraping Match Report Section ---")
            #scrape_match_report(soup)
            
            #print("\n--- Scraping Scores Section ---")
            #scrape_scores(soup)
            
            #print("\n--- Scraping Line-ups Section ---")
            #scrape_lineups(soup)
            
            #print("\n--- Scraping Match Stats Section ---")
            #scrape_match_stats(soup)
            
            #print("\n--- Scraping Head-to-Head Section ---")
            #scrape_head_to_head(soup)


if __name__ == "__main__":
    main()
