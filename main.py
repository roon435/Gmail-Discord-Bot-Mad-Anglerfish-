import os
import discord
from discord import app_commands
import asyncio
import aiosmtplib
from email.message import EmailMessage

# Get credentials from env vars (Railway-friendly)
TOKEN = os.getenv("TOKEN")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

if not TOKEN or not GMAIL_USER or not GMAIL_PASS:
    print("Missing one or more environment variables: TOKEN, GMAIL_USER, GMAIL_PASS")
    exit(1)

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = MyClient()

@client.tree.command(name="gmail", description="Send emails via Gmail")
@app_commands.describe(
    email="Recipient's Gmail address",
    message="Message content to send",
    count="Number of messages to send (max 20)"
)
async def gmail(interaction: discord.Interaction, email: str, message: str, count: int = 1):
    await interaction.response.defer(thinking=True)

    if count < 1:
        await interaction.followup.send("Count must be at least 1.")
        return
    if count > 20:
        await interaction.followup.send("Limit is 20 messages per command to avoid abuse.")
        return

    sent = 0
    errors = 0

    for _ in range(count):
        email_message = EmailMessage()
        email_message["From"] = GMAIL_USER
        email_message["To"] = email
        email_message["Subject"] = "Message from Discord Bot"
        email_message.set_content(message)

        try:
            await aiosmtplib.send(
                email_message,
                hostname="smtp.gmail.com",
                port=587,
                start_tls=True,
                username=GMAIL_USER,
                password=GMAIL_PASS,
            )
            sent += 1
            await asyncio.sleep(1)  # polite delay
        except Exception as e:
            errors += 1

    await interaction.followup.send(f"Sent {sent} emails. Errors: {errors}.")

client.run(TOKEN)
