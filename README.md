# Bluesky Discord Monitor
A cheap Python script that monitors Bluesky author feeds for new posts and replies, and then relays them to Discord via webhooks. All setup is done in **config.json**, and author feeds are defined by their Decentralized Identifier (DID). 

This isn't my best code, and I made this in about 3 hours, and it's my first public repository. So if you'd like to make changes or fork it, please feel free to do so!

# Setup
### Windows:
1. Download a .ZIP archive of the repository. Extract to your preferred location.
2. Download and install [Python 3.10 or greater.](https://www.python.org/downloads/) You can also get Python from the [Microsoft Store](https://apps.microsoft.com/detail/9pjpw5ldxlz5?hl=en-us&gl=US)
3. Open a **Command Prompt (or Powershell) terminal** and cd to the directory where you extracted the code, and then run:
    ```powershell
    python -m pip install -r requirements.txt
    ```
    This will install all of the required libraries for the script.
4. [Set up your configuration.](https://github.com/MissMeridian/bluesky-discord-monitor/tree/main/README.md#configuration) Continue these steps when finished.
5. Open **main.py** or the **loop.bat** batch script. If there is an error, the **loop.bat** script will restart the Python code on its own.

### Linux:
1. Download a .ZIP archive of the repository. Extract to your preferred location.
2. Install Python 3 with your package manager, if not already installed.
3. Create a virtual environment somewhere in the location where you extracted the code:
    ```bash
    python3 -m venv .venv
    ```
4. With the new virtual environment created, install the requirements:
    ```bash
    .venv/bin/pip install requirements.txt
    ```
5. [Set up your configuration.](https://github.com/MissMeridian/bluesky-discord-monitor/tree/main/README.md#configuration) Continue these steps when finished.
6. Run **main.py** with the virtual environment:
    ```bash
    .venv/bin/python3 main.py
    ```

If you are running this on a server you may want to consider [setting up a systemd service](https://www.linux.org/threads/how-to-create-a-custom-systemd-service-file.47399/) so that it runs in the background and restarts automatically. The best way to do this is to set up a shell script that runs the Python script in the virtual environment. I provided a sample file called **loop.sh** that you can use to do this.

# Configuration
Configuration isn't so difficult as long as you don't make a typo in the JSON file. There are a few things you need to do before we can edit the config.
### Create a bot account
Although not *required,* you should create a bot account so that you don't rate-limit your main account. [Sign up with a new account](https://bsky.app/) like usual. (You can use your own PDS if you'd like, but you will need to change the **xrpc_url** value in the config to your PDS if you do so.)
### Place the login credentials in config.json
- In **config.json**, edit the value for **"handle"** with the username handle for your bot **(e.g. "cool-bot.bsky.social")**. Keep it inside the quotation marks.
- In **config.json**, edit the value for **"password"** with the login password for your bot **(e.g. "V3RY#$3CUR3")**. Keep it inside the quotation marks. 
### Set up monitored accounts
The **"monitors"** object works like a dictionary of user IDs, and each user ID object contains a list of Discord webhook URLs. For example:

    "monitors": {
        "did:plc:this-is-my-user-did": ["https://a-discord-webhook","https://another-webhook-because-why-not"],
        "did:plc:my-cool-friend's-did": ["https://a-discord-webhook"]
    }

There are two parts to this. Getting the user DID, and setting up a Discord webhook.

**1. Get the user DID.**

 If you want to get your own DID, this is easy. In Bluesky, [go to **Settings**](https://bsky.app/settings), and click on **Change Handle** under "Advanced". Then click on the blue text on the box that appears that says "**I have my own domain**". A DNS record text appears in the middle. Underneath where it says **Value:**, you'll see a string of text that looks something like "**did=did:plc:blahblahblahblahblah**". Copy everything after "**did=**" and you should have just the "**did:plc:blahblahblah**" part. Paste this into the **config.json** file in the "monitors" object, formatted properly as explained above.

 If you want to get somebody else's DID, the easiest way is to use [this tool](https://bluesky-id.fermyon.app/). However, this may not work for users who have their handle tied to their own PDS.

**2. Create a Discord webhook.**

In a Discord server that you have admin permissions in, edit the desired text channel you want the posts relayed in. Go to **Integrations,** and click on **Webhooks.** Create a **New Webhook.** Click on the new webhook you just created, and it should expand with more options. Click on **Copy Webhook URL**. 
    
Paste the URL (that you just copied) into the list associated with the desired DID.

The list corresponding to the DID inside of "**monitors**" contains the URLs where monitored posts from that DID will be relayed. You can have more than one webhook in each list, and it's done this way in order to save on Bluesky API usage and prevent being rate limited if you want to relay your posts to multiple channels. There is a 3 second timeout for each Discord message so that the bot doesn't get rate limited by Discord's API.

**The "monitors" section should look something like the example above depending on how many webhooks you attached.**

### Additional config values:

#### xrpc_url
The URL to the Personal Data Server (PDS). This is https://bsky.social by default unless you run your own.

#### search_range
The number of recent posts that will be pulled from an author's feed. This value can be adjusted (must be a whole integer), but please keep rate limits in mind.

#### wait_time
The time to wait in seconds before pulling new posts. Again, if you change this value, be mindful of rate limiting.

# Known Issues
- Replies and posts are not distinguished in the Discord messages. I have not yet figured out how to determine the FeedViewPost context to distinguish the two.

If you find any other issues or bugs, [please report it in Issues!](https://github.com/MissMeridian/bluesky-discord-monitor/issues)



### Hopefully I explained everything well enough. Please don't hesitate to ask questions if you need help. I'm not a professional, and I make mistakes frequently!
