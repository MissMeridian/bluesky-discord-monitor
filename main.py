from atproto import Client
import json, logging, time, os
from discord_webhook import DiscordEmbed, DiscordWebhook
from datetime import datetime, timezone

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
log.addHandler(console_handler)

def initialize_archive():
    with open("archived.json", "w") as archived_file:
        new_json = {"archived": []}
        json.dump(new_json, archived_file)
        archived_file.close()

def mark_archived(post_url):
    if not os.path.exists("archived.json"):
        initialize_archive()
    with open("archived.json", "r") as archived_file:
        archive = json.load(archived_file)
        archived_file.close()
    archived = list(archive["archived"])
    archived.append(post_url)
    new_json = {"archived": archived}
    with open("archived.json", "w") as archived_file:
        json.dump(new_json, archived_file)
        archived_file.close()

def check_archive(post_url):
    if not os.path.exists("archived.json"):
        initialize_archive()
    with open("archived.json", "r") as archived_file:
        archive = json.load(archived_file)
        archived_file.close()
    if post_url in archive["archived"]:
        return True
    else:
        return False

def discord_embed(webhook_urls, display_name, handle, avatar, post_url, text, images, alts, timestamp):
    for webhook_url in webhook_urls:
        name = f"{display_name} ({handle})"
        profile = f"https://bsky.app/profile/{handle}"
        
        webhook = DiscordWebhook(url=webhook_url, username=handle, avatar_url=avatar)
        embed = DiscordEmbed(title=f"New post from {display_name}!", description=text, color="1083fe", url=post_url)
        embed.set_author(name=display_name, url=profile, icon_url=avatar)
        if images:
            image = images[0]
            embed.set_image(url=image)
        embed.set_thumbnail(url="https://bsky.app/static/favicon-16x16.png")
        embed.set_timestamp(timestamp=timestamp)
        if alts:
            alt = alts[0]
            embed.set_footer(text=alt)
        webhook.add_embed(embed=embed)
        webhook.execute()
        time.sleep(3) # Wait a few seconds before continuing so that we don't exceed the Discord Webhook rate limit.

def login_client():
    log.debug("Loading config.json")
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        USER = config["handle"] # Username/handle (e.g. test.bsky.social)
        PASS = config["password"] # Password
        XRPC = config["xrpc_url"] # XRPC URL (default is https://bsky.social - the URL to the ATprotocol PDS)
    log.debug(f"Attempting to log in to {USER} on {XRPC}")
    client = Client(base_url=XRPC)
    client.login(login=USER, password=PASS)
    log.info(f"Login succeeded.")
    return client

def get_feed(client: Client, did: str, whooks: list, search_range: int):
    post_data = client.get_author_feed(actor=did, limit=search_range, filter="posts_with_replies")
    #print(f"POST DATA: \n{post_data}\n\n")
    feed = post_data.feed
    #print(f"FEED:\n{feed}\n\n")
    for post_item in feed:
        try:
            post = post_item.post
            author = post.author
            author_name = getattr(author, 'display_name', 'Unknown Author')  # Use dot notation
            author_handle = getattr(author, 'handle', 'Unknown Handle')
            author_avatar = getattr(author, 'avatar', None)
            post_uri = getattr(post, 'uri', 'No URI available')
            post_id = post_uri.split('/')[-1]  # Extract the post ID from the URI
            post_url = f"https://bsky.app/profile/{author_handle}/post/{post_id}"
            author_did = post_uri.split('/')[2] # Extract the DID from the URI
            if author_did == did:
                is_archived = check_archive(post_url)
                if not is_archived:
                    log.info(f"New post from {author_handle} detected! ({post_url})")
                    record = post.record
                    post_text = getattr(record, 'text', 'No text available')
                    record_timestamp = getattr(record, 'created_at', "1969-12-31T00:00:00.000Z")
                    date_obj = datetime.strptime(record_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
                    date_obj = date_obj.replace(tzinfo=timezone.utc)
                    timestamp = date_obj.timestamp()
                    embed = post.embed
                    try:
                        # Try for embedded images. Sometimes this will call an exception if there are none.
                        images = embed.images if embed else []
                        image_urls = []
                        image_alts = []
                        for image in images:
                            image_urls.append(image.fullsize) # Append fullsize image URL 
                            image_alts.append(image.alt)
                    except:
                        log.debug("No image attached.")
                        images = None
                        image_urls = []
                        image_alts = []
                        try: 
                            # Try for embedded videos, and pull a thumbnail if available.
                            image_urls.append(embed.thumbnail)
                        except:
                            log.debug("No video attached.")
                    mark_archived(post_url)
                    discord_embed(whooks, author_name, author_handle, author_avatar, post_url, post_text, image_urls, image_alts, timestamp)
                else:
                    log.info(f"{post_url} already archived. Not posting!")
            else:
                log.info(f"{post_url} is a repost or liked post, and will be ignored since it was not posted by the monitored DID.")
        except Exception:
            log.error(f"Unexpected error occured while processing a post! Report this on the GitHub please!\n", exc_info=True)

def pull_loop():
    while True:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
            wait_time = config["wait_time"]
        for did in config["monitors"]:
            get_feed(client=client, did=did, whooks=config["monitors"][did], search_range=config["search_range"])
        config_file.close()
        time.sleep(wait_time)
    
try:
    client = login_client()
    pull_loop()
except Exception as e:
    log.error("Error occurred while attempting to log in to Bluesky!", exc_info=True)
    time.sleep(600) # Let's not get rate limited trying to log in 1,000 times.



