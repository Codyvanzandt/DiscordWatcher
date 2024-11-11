# monitor.py
import discord
from discord.ext import tasks
from datetime import datetime
import os
from dotenv import load_dotenv
import resend

load_dotenv()

class DiscordMonitor(discord.Client):
    def __init__(self):
        # Fix: Add intents
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(self_bot=True, intents=intents)  # Added intents here
        
        resend.api_key = os.getenv('RESEND_API_KEY')
        self.channel_id = int(os.getenv('CHANNEL_ID'))
        self.last_message_time = datetime.now().timestamp()

    async def setup_hook(self):
        self.check_messages.start()

    @tasks.loop(seconds=15)
    async def check_messages(self):
        channel = self.get_channel(self.channel_id)
        if not channel:
            print(f'Could not find channel {self.channel_id}')
            return

        after = datetime.fromtimestamp(self.last_message_time)
        async for message in channel.history(after=after, limit=10):
            await self.send_notification(message)
            self.last_message_time = message.created_at.timestamp()

    async def send_notification(self, message):
        content = f"""
New message in {message.channel.name}
From: {message.author}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Content:
{message.content}
        """

        try:
            r = resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": "cody.a.vanzandt@gmail.com",
                "subject": f"Discord Update - {message.channel.name}",
                "text": content,
            })
            print(f'Email sent: {message.content[:50]}...')
        except Exception as e:
            print(f'Failed to send email: {str(e)}')

    async def on_ready(self):
        print(f'Logged in successfully')
        print(f'Monitoring channel: {self.channel_id}')
        print('Press Ctrl+C to exit')

if __name__ == "__main__":
    required_vars = ['USER_TOKEN', 'RESEND_API_KEY', 'CHANNEL_ID']
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        exit(1)

    client = DiscordMonitor()
    client.run(os.getenv('USER_TOKEN'))