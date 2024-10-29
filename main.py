import requests
from bs4 import BeautifulSoup
import time
import os
from openai import OpenAI
from pathlib import Path
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv
import pygame


load_dotenv()

client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

# Function to scrape Live Text section
def scrape_live_text(soup):
    live_text = []
    live_text_section = soup.find(id='LiveText')
    if live_text_section:
        for li in live_text_section.find_all('li'):
            timestamp_span = li.find('span', {'data-testid': 'accessible-timestamp'})
            title_span = li.find('span', {'role': 'text'})
            p_tag = li.find('p')
            
            if timestamp_span and p_tag:
                timestamp = timestamp_span.get_text(strip=True)
                title = title_span.find('span', recursive=False).get_text(strip=True) if title_span else None
                if title == "Post":
                    title = None
                text = p_tag.get_text(strip=True)
                live_text.append(f"{timestamp} - {title if title != None else ""} {text}")
    return live_text

# Function to scrape Match Report section
def scrape_match_report(soup):
    report_section = soup.find(id='Report')
    if report_section:
        for p in report_section.find_all('p'):
            print(p.get_text(strip=True))

# Function to scrape Scores section
def scrape_scores(soup):
    hometeam = ""
    awayteam = ""
    hometeamscore = 0
    awayteamscore = 0
    venue = ""
    # Scrape header info for team names and stadium
    header_info = soup.find(id='live-header-aside-content')
    if header_info:
        # Extract home team name
        home_team = header_info.find("div", class_=lambda x: x and 'TeamHome' in x)
        if home_team:
            home_team_name = home_team.find("span", class_=lambda x: x and 'DesktopValue' in x)
            if home_team_name:
                hometeam = home_team_name.get_text(strip=True)
        
        # Extract away team name from span with class containing 'DesktopValue'
        away_team = header_info.find("div", class_=lambda x: x and 'TeamAway' in x)
        if away_team:
            away_team_name = away_team.find("span", class_=lambda x: x and 'DesktopValue' in x)
            if away_team_name:
                awayteam = away_team_name.get_text(strip=True)
        
        # Extract stadium name
        stadium = header_info.find("div", class_=lambda x: x and 'Venue' in x)
        if stadium:
            venue = stadium.get_text(strip=True)

        
        # Extract stadium name
        home_score = header_info.find("div", class_=lambda x: x and 'HomeScore' in x)
        away_score = header_info.find("div", class_=lambda x: x and 'AwayScore' in x)

        if home_score:
            hometeamscore = home_score.get_text(strip=True)
        if away_score:
            awayteamscore = away_score.get_text(strip=True)
    return hometeam, awayteam, hometeamscore, awayteamscore, venue

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

def speak_text(text, hometeam, awayteam, hometeamscore, awayteamscore, venue):
    # Generate commentary text
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a english football (soccer) radio commentator. use the data provided to say something like a commentator. (Match details: home team = {hometeam}, away team = {awayteam}, home team score = {hometeamscore}, away team score = {awayteamscore}, {venue})"},
            {"role": "user", "content": text}
        ]
    )
    commentary = completion.choices[0].message.content
    print(commentary)

    # Set file path for audio
    speech_file_path = Path(__file__).parent / "speech.mp3"

    # Generate audio
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=commentary,
    ) 

    response.stream_to_file(speech_file_path)

    # Load and play the audio file
    audio = AudioSegment.from_mp3(speech_file_path)
    play(audio)


def generate_commentary(live_text):
    #prompt = f"Convert the following live text into sports commentary from a pundit: {live_text}"
    #response = generator(prompt, max_length=100, num_return_sequences=1)
    #commentary = response[0]['generated_text']
    return live_text

# Function to play background music
def play_music():
    pygame.mixer.init()
    pygame.mixer.music.load('background_crowd.mp3')  # Replace with your MP3 file path
    pygame.mixer.music.set_volume(0.1)  # Optional volume adjustment
    pygame.mixer.music.play(-1)  # Play indefinitely

# Main function to scrape and print content
def main():
    play_music()

    base_url = "https://www.bbc.co.uk/sport/football/live/crln8pjzjxet"
    
    processed_entries = set()  # Store processed entries here
    
    # Loop to rescrape indefinetly
    while True:
        print("\n--- Starting new scrape cycle ---")
        
        soup = fetch_and_parse(base_url)
        
        if soup:
            print("Soup successfully fetched.")
            hometeam, awayteam, hometeamscore, awayteamscore, venue = scrape_scores(soup)
            live_text = scrape_live_text(soup)
            live_text = live_text[:5]
            print(f"Live text entries scraped: {len(live_text)}")

            # Filter out entries that have already been processed
            new_entries = [entry for entry in live_text if entry not in processed_entries]
            
            print(f"New entries to process: {len(new_entries)}")

            if new_entries:
                for entry in new_entries[::-1]:  # Reverse to process newest first
                    speak_text(entry, hometeam, awayteam, hometeamscore, awayteamscore, venue)

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
