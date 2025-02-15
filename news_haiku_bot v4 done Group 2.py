import random
import textstat
import requests
from discord_webhook import DiscordWebhook
from bs4 import BeautifulSoup
from datetime import datetime
import schedule
import time

# Replace with your actual Discord WebHook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1340337020630732921/HfRaDmOn4YtqGqUFgsfJALpXw4MmoMVWa3jeqtiH_raW_BFYhuiy0HxH-TYW8beNjPNf"

# Define the times you want the bot to post (24-hour format)
POST_TIMES = ["09:00", "18:00"]  # Example: 9:00 AM and 6:00 PM

def get_news_from_website():
    """Fetches news headlines from BBC and filters valid ones."""
    try:
        url = "https://www.bbc.com"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Scraping headlines from BBC
        headlines = [headline.get_text().strip() for headline in soup.find_all(['h1', 'h2', 'h3'])]

        # Remove non-news headlines
        ignored_phrases = ["Editor's Picks", "Sign up", "Breaking News", "Live Updates"]
        headlines = [h for h in headlines if not any(phrase in h for phrase in ignored_phrases)]

        # Filter out headlines that exceed the syllable limit
        headlines = [h for h in headlines if count_syllables(h) <= 20]

        return headlines[:50]  # Adjust number of headlines if needed
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def count_syllables(text):
    """Counts syllables in a given text using textstat."""
    return textstat.syllable_count(text)

def create_haiku(headlines):
    """Creates a haiku (5-7-5) from news headlines."""
    
    # Stricter syllable filtering
    five_syllable = [h for h in headlines if count_syllables(h) == 5]
    seven_syllable = [h for h in headlines if count_syllables(h) == 7]

    if len(five_syllable) >= 2 and len(seven_syllable) >= 1:
        haiku = f"{random.choice(five_syllable)}\n{random.choice(seven_syllable)}\n{random.choice(five_syllable)}\n~ Group 2"
        return haiku
    return None  # Return None if a valid haiku cannot be formed

def send_to_discord(haiku):
    """Sends the haiku to a Discord channel via WebHook and prints the timestamp."""
    if haiku:
        try:
            current_time = datetime.now().strftime("%H:%M")
            webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=f"**Haiku posted at {current_time}:**\n\n{haiku}")
            webhook.execute()
            print(f"Haiku posted at {current_time}:\n{haiku}")
        except Exception as e:
            print(f"Error sending message to Discord: {e}")
    else:
        print("No valid haiku could be formed. Skipping post.")

def job():
    """Fetch news, generate a haiku, and post it now."""
    headlines = get_news_from_website()
    
    if not headlines:
        print("No headlines found. Exiting.")
        return

    haiku = create_haiku(headlines)
    send_to_discord(haiku)

def schedule_jobs():
    """Schedule the job to post at specific times."""
    for post_time in POST_TIMES:
        schedule.every().day.at(post_time).do(job)
        print(f"Scheduled a post at {post_time}")

def main():
    """Main function to schedule and run jobs."""
    schedule_jobs()
    
    while True:
        schedule.run_pending()
        time.sleep(1)  # Wait for the next scheduled time

if __name__ == "__main__":
    main()
