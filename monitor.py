# monitor.py
import requests
from bs4 import BeautifulSoup
import time
import hashlib
import os
from dotenv import load_dotenv
import resend
from datetime import datetime

load_dotenv()

class LeaguesMonitor:
    def __init__(self):
        self.url = "https://secure.runescape.com/m=news/leagues-v-teasers--faqs---releasing-november-27th?oldschool=1"
        resend.api_key = os.getenv('RESEND_API_KEY')
        self.last_hash = None
        
    def get_content(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(self.url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get entire article content div
            content = soup.find('div', class_='news-article-content')
            return str(content) if content else None

        except Exception as e:
            print(f"Error fetching content: {str(e)}")
            return None

    def get_content_hash(self, content):
        if not content:
            return None
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def send_notification(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            r = resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": "cody.a.vanzandt@gmail.com",
                "subject": "OSRS Leagues V Update!",
                "text": f"""
Change detected on the Leagues V page!
Time: {current_time}

Check it out here:
{self.url}

The page content has been updated - there might be a new reveal!
                """
            })
            print(f'Email notification sent at {current_time}!')
        except Exception as e:
            print(f'Failed to send email: {str(e)}')

    def check_for_changes(self):
        try:
            content = self.get_content()
            if not content:
                print("Failed to get content")
                return
            
            current_hash = self.get_content_hash(content)
            current_time = datetime.now().strftime("%H:%M:%S")
            
            if self.last_hash is None:
                self.last_hash = current_hash
                print(f"[{current_time}] Initial content hash stored. Monitoring for changes...")
                return
            
            if current_hash != self.last_hash:
                print(f"[{current_time}] Change detected!")
                self.send_notification()
                self.last_hash = current_hash
            else:
                print(f"[{current_time}] No changes detected")
                
        except Exception as e:
            print(f"Error checking for changes: {str(e)}")

    def run(self):
        print("Starting Leagues V monitor...")
        print(f"Monitoring URL: {self.url}")
        print("Checking every 15 seconds")
        print("Press Ctrl+C to exit")
        
        while True:
            self.check_for_changes()
            time.sleep(15)

if __name__ == "__main__":
    if not os.getenv('RESEND_API_KEY'):
        print("Error: RESEND_API_KEY is required in .env file")
        exit(1)

    monitor = LeaguesMonitor()
    monitor.run()