import nextcord as discord
from nextcord.ext import tasks, commands
import cfscrape
import traceback
import json
import requests
from datetime import datetime
import asyncio

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
interval = 60 * 2   # Set this to your desired interval in minutes

channel_id_1 = 1185841250616750090  # The ID of the channel where messages will be sent (from Code1)
channel_id_2 = 1205750107459551242  # The ID of the channel to send messages (from Code2)

api_url = "https://api.comick.io/v1.0/search?limit=49&page=1"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    scrape_and_send.start()
    send_comic_link.start()
    fetch_data_and_send_messages.start()
  #  follow_chapter_time_difference.start()


@bot.command(name='addcomic')
async def add_comic(ctx, comic_id: str, limit: int = 3):  # limit is optional, default is 3
    try:
        with open('subscriptions.json', 'r') as f:
            subscriptions = json.load(f)

        user_id = str(ctx.message.author.id)
        new_entry = {"comic_id": comic_id, "limit": limit}

        subscriptions.setdefault(user_id, []).append(new_entry)

        with open('subscriptions.json', 'w') as f:
            json.dump(subscriptions, f, indent=4)

        await ctx.send(f"Successfully added {comic_id} to the subscription list.")
    except Exception as e:
        await ctx.send(f"An error has occurred: {e}")

@bot.command(name='checkid')
async def check_comic_id(ctx, *, manga_title: str):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        api_url = f"https://api.comick.fun/comic/{manga_title}"
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            json_data = response.json()
            comic_data = json_data.get('comic')
            
            # Check if comic_data is None before using get()
            if comic_data is not None:
                hid = comic_data.get('hid') if isinstance(comic_data, dict) else None

                if hid is not None:
                    await ctx.send(f"The HID for the manga '{manga_title}' is: {hid}")
                else:
                    await ctx.send(f"Could not find the HID for the manga '{manga_title}'. The response might have changed.")
                    print(f"Failed to extract HID for {manga_title}. The response might have changed or the key does not exist.")
            else:
                await ctx.send(f"No data received for '{manga_title}'.")
                print(f"No data received for {manga_title}.")

        elif response.status_code == 403:
            print(f"Access denied when trying to reach {api_url}. The server returned a 403 Forbidden status.")
            await ctx.send("Sorry, access to the comic information was denied. This could be due to server restrictions.")
        else:
            await ctx.send(f"Could not find a comic with the title '{manga_title}'. Please check the title and try again.")
            print(f"Received a {response.status_code} status for {api_url}")

    except Exception as e:
        error_message = f"An error has occurred while processing '{manga_title}': {traceback.format_exc()}"
        print(error_message)
        await ctx.send(error_message)

@bot.command(name='removecomic')
async def removecomic(ctx, comic_id):
    # Get user ID
    user_id = str(ctx.author.id)

    # Read subscriptions.json file
    with open('subscriptions.json', 'r') as file:
        subscriptions = json.load(file)

    # Check if user_id exists in subscriptions
    if user_id in subscriptions:
        # Iterate through user's subscriptions
        for i, comic_entry in enumerate(subscriptions[user_id]):
            # If comic_id matches current entry's comic_id
            if comic_entry['comic_id'] == comic_id:
                # Remove entry from user's subscriptions
                del subscriptions[user_id][i]
                # Write updated subscriptions to subscriptions.json file
                with open('subscriptions.json', 'w') as file:
                    json.dump(subscriptions, file, indent=4)
                # Send success message
                await ctx.send("Comic successfully removed from subscriptions.")
                return
        # If no matching comic_id was found
        await ctx.send("Comic not found in your subscriptions.")
    else:
        # If user has no subscriptions
        await ctx.send("You have no subscriptions.")

@tasks.loop(minutes=180)
async def fetch_data_and_send_messages():
    try:
        scraper = cfscrape.create_scraper()
        response = scraper.get(api_url, headers={'User-Agent': user_agent})
        response.raise_for_status()  

        data = response.json()
        print("Data from API:", data)

        channel = bot.get_channel(channel_id_2)
        
        for entry in data[:5]:  
            hid = entry.get("hid")
            slug = entry.get("slug")
            title = entry.get("title")
            uploaded_at = datetime.strptime(entry.get("uploaded_at", ""), "%Y-%m-%dT%H:%M:%S.%fZ")
            created_at = datetime.strptime(entry.get("created_at", ""), "%Y-%m-%dT%H:%M:%S.%fZ")
            mu_comics = entry.get("mu_comics")

            if mu_comics is not None:
                year = mu_comics.get("year")
            else:
                year = None

            message = f"`hid`: {hid}\n`slug`: {slug}\n`title`: {title}\n`uploaded_at`: {uploaded_at}\n`created_at`: {created_at}\n`year`: {year}"
            await channel.send(message)

    except Exception as e:
        print("Error fetching data from API:", e)

    except Exception as e:
        print("Error fetching data from API:", e)

@tasks.loop(minutes=interval)
async def scrape_and_send():
    try:
        scraper = cfscrape.create_scraper()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        channel_id = 1185841250616750090  

        with open('subscriptions.json', 'r') as f:
            subscriptions = json.load(f)

        for discord_id, sub_list in subscriptions.items():
            try:
                for sub in sub_list:  
                    limit = 5  
                    response = scraper.get("https://api.comick.io/chapter?accept_erotic_content=true&page=1&device-memory=8&order=new", headers=headers)
                    data = response.json()

                    if isinstance(data, list):
                        chapters = data[:limit]

                        for chapter in chapters:
                            comic = chapter.get('md_comics', {})
                            title = comic.get('title', 'N/A')
                            comic_id = comic.get('hid', 'N/A') 
                            country = comic.get('country', 'N/A')
                            site_publish_date = comic.get('created_at', 'N/A')

                            chap_num = chapter.get('chap', 'N/A')
                            vol = chapter.get('vol', 'N/A')
                            updated_at = chapter.get('updated_at', 'N/A')

                            info = (
                                f"Title: {title}\n"
                                f"Comic ID: {comic_id}\n"
                                f"Country: {country}\n"
                                f"Site Publish Date: {site_publish_date}\n"
                                f"Chapter: {chap_num}\n"
                                f"Volume: {vol}\n"
                                f"Chapter Update Date: {updated_at}"
                            )

                            channel = bot.get_channel(channel_id)
                            await channel.send(info)
            except Exception as e:
                print(f"Error processing user subscriptions: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

@tasks.loop(hours=7)
async def send_comic_link():
    try:
        with open('subscriptions.json', 'r') as f:
            subscriptions = json.load(f)

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

        for discord_id, sub_list in subscriptions.items():
            for sub in sub_list:
                try:
                    comic_id = sub.get("comic_id")
                    limit = sub.get("limit", 5)  

                    url = f"https://comick.io/comic/{comic_id}"
                    response = requests.get(f"https://api.comick.fun/comic/{comic_id}/chapters?lang=en", headers=headers)

                    if response.status_code == 200:
                        data = response.json()
                        chapters = data.get('chapters', [])

                        if isinstance(chapters, list):  
                            chapters = chapters[:limit]

                            for chapter in chapters:
                                chap_num = chapter.get('chap', 'N/A')
                                created_at = chapter.get('created_at', 'N/A')
                                updated_at = chapter.get('updated_at', 'N/A')
                                group_name = chapter.get('group_name', 'N/A')

                                user = await bot.fetch_user(int(discord_id))

                                await user.send(
                                    f"Comic link: {url}\nChapter: {chap_num}\nPublished at: {created_at}\nUpdated at: {updated_at}\nScanlated by: {group_name}"
                                )
                    else:
                        print(f"Failed to fetch comic data for comic ID {comic_id}. Response status code: {response.status_code}")

                except Exception as e:
                    print(f"An error occurred: {e}")

    except Exception as e:
        print(f"An error occurred while processing subscriptions: {e}")

@tasks.loop(minutes=interval)
async def follow_chapter_time_difference():
    try:
        scraper = cfscrape.create_scraper()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        channel_id = 1205750107459551242  # Replace with the appropriate channel ID
        print("Sending request to API...")
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: scraper.get("https://api.comick.io/user/follow/chapter", headers=headers))
        
        print(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Full response data:")
            print(json.dumps(data, indent=4))
            if "data" in data and data["data"]:
                chapters = data["data"]
                print(f"Received {len(chapters)} chapter(s)")
                for chapter_data in chapters:
                    title = chapter_data['md_comics']['title']
                    slug = chapter_data['md_comics']['slug']
                    chap = chapter_data['chap']
                    distance_time = chapter_data['distanceTime']
                    message = f"Title: {title}\nSlug: {slug}\nChapter: {chap}\nUploaded: {distance_time} ago"
                    channel = bot.get_channel(channel_id)
                    if channel:
                        await channel.send(message)
                    else:
                        print(f"Channel with ID {channel_id} not found")
            else:
                print("No chapters found in the response data.")
        else:
            print(f"Failed to retrieve data from the API. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

bot.run('-')
