# etc-project
showing comick webmaster that there isn't nothing suspicious in regards of what i am doing

# How this works
I have made a script where basically a user can check comic_id on what slug tag it has 

[!checkid command](https://raw.githubusercontent.com/projectstuff2/etc-project/main/image.png)
what the checkid command do is that it would scrape comick's api to see if there are any slugs relating to the manga title to translate to comic_id

Chatlogs how it works:
!checkid mi-chan-wa-kawaretai

BOT
 — 03/04/2024 10:33 AM
The HID for the manga 'mi-chan-wa-kawaretai' is: gN8joy3V

Wavey — 03/04/2024 10:33 AM
!addcomic gN8joy3V

BOT
 — 03/04/2024 10:33 AM
Successfully added gN8joy3V to the subscription list.

[scraping api's to check new chapters](https://i.ibb.co/QY7bjQZ/image.png)

in 'scrape_and_send' function, what this does is that it would scrape this api endpoint, 'chapter?accept_erotic_content=true&page=1&device-memory=8&order=new', to see if there are any new changes every interval (refer to the variable 'interval'). 
if there is any new chapter, it would sent to this channel id (linked to the image), 1185841250616750090.

```python
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

```
this is what the code looks like ^


this is what the user see
```
Title: Time Traveler
Comic ID: r2Z86wED
Country: kr
Site Publish Date: 2023-11-10T14:07:17.766Z
Chapter: 29
Volume: None
Chapter Update Date: 2024-04-13T09:43:06.508Z
```

For the subscribing '!addcomic', if every user id subscribe to a comic id, it would submit it to the subscriptions.json

its something like this
```json
{
    "365659613821009920": [
        {
            "comic_id": "uTrdHTHN",
            "limit": 3
        },
        {
            "comic_id": "bXUxIbHc",
            "limit": 3
        },
        {
            "comic_id": "pws_rHUb",
            "limit": 3
        },
        {
            "comic_id": "s5HY60Uo",
            "limit": 3
        },
        {
            "comic_id": "7qgFowKg",
            "limit": 3
        },
        {
            "comic_id": "mmUDdh3L",
            "limit": 3
        },
        {
            "comic_id": "eCuLZtr3",
            "limit": 3
        },
        {
            "comic_id": "U17RgAgc",
            "limit": 3
        },
        {
            "comic_id": "UctVel7Y",
            "limit": 3
        },
        {
            "comic_id": "gvKLTHrE",
            "limit": 3
        },
        {
            "comic_id": "BuFOeEhX",
            "limit": 3
        },
        {
            "comic_id": "gN8joy3V",
            "limit": 3
        }
    ]
}
```

365659613821009920 - this discord id refer to 'Wavey'

comic_id - refers to the comic id to use for the url 'comick.io/comic/{the actual id}'

when the user submits '!addcomic {id}' what it would do is that the bot would know that user has submitted the new log or entries to put it to the json file to allow it to start checking over the api at specific interval.

which it would send through this function
```
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
```
this function checks if there are any new chapters following how much the bot can send at what 'limit' (refer to the json file), 


this is what it looks like for the user
```
Comic link: https://comick.io/comic/gN8joy3V
Chapter: 10
Published at: 2024-01-18T13:49:41Z
Updated at: 2024-04-10T07:39:14Z
Scanlated by: ['Shadow-sama Scans']
```

for the developer
```python
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
```

all of the other function like this are rather not been used or will not plan on to be pushed
```python
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
```

this is how it basically works.
it uses cfscrape to bypass cloudflare, which has been a pytohn package https://pypi.org/project/cfscrape/
why i am showing you this is because, i am not doing anything malicious and yes, while it did send out alot of request. i will implant on putting some interval to the variable so it could connect with it rather then individual interval for each function.

Domains that are involved

api.comick.fun - been used for a little before shutting the script down to write this

api.comick.io - main api used for scraping and checking

cloudflare ray id: 873a8e353f93532b
