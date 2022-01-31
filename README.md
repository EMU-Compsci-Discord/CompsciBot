# Welcome to the new and improved CompsciBot!



## Getting started 

This is a tutorial for new developers who have never made or setup a discord bot 
before.

### Prior Knowledge:

This tutorial assumes you have a basic understanding of GitHub,  and python. It also assumes you have git and python installed on your computer.

If you do not have this skill yet, we recommend you check out:

 - [An Intro to Git and GitHub for Beginners](https://product.hubspot.com/blog/git-and-github-tutorial-for-beginners)
 - [Python for Beginners](https://www.python.org/about/gettingstarted/)
 - [IDEs and Text Editors](https://www.pythondiscord.com/resources/tools/) 
 
 **Note:** we will be using Visual Studio Code in this tutorial

### 1. Getting the Code

First things first, we will need to clone the main GitHub to our local repository.
 
One way to do this is to paste this code in terminal, where you want the files to go:
``` 
git clone https://github.com/Nanosplitter/CompsciBot 
```
You should see something similar to this result if you are using Windows Command Prompt, but the command will work on Mac and Linux aswell.

<img src="https://github.com/Nanosplitter/CompsciBot/blob/dev/readme/imgs/cmdCloneCommand.png" alt="Command Line Output"/>

### 2. Getting a Discord Bot
Now that you have the code base, you need to add a bot to discord to test any new code you add.

You should see an interface like this one:
<img src="https://github.com/Nanosplitter/CompsciBot/blob/dev/readme/imgs/devPortal.png" alt="Discord Developer Website"/>

Click on "New Application" in the top right.

You will be prompted to give it a name, we suggest using "CompsciBot - [your name]".

<img src="https://github.com/Nanosplitter/CompsciBot/blob/dev/readme/imgs/devAppName.png" alt="Adding a Name"/>

You will then be taken to the bots General information.  Note the **APPLICATION ID**, as its important for later.

<img id="appId" src="https://github.com/Nanosplitter/CompsciBot/blob/dev/readme/imgs/appMain.png" alt="General Application Page"/>

### 3. Adding a Bot 
Now that you have an application, you need the actual bot.  

Click on the Bot tab in the sidebar to see this:

<img src="https://github.com/Nanosplitter/CompsciBot/blob/dev/readme/imgs/appBot.png" alt="Application Bot Page"/>

Click "Add Bot". The page will ask if you are sure, click "Yes".

Now you will see a Bot Screen, with the default discord logo and name.


Notice the **TOKEN** section of the page, as we will use that in the next step.
<img id="token" src="https://github.com/Nanosplitter/CompsciBot/blob/dev/readme/imgs/botScreen.png" alt="Bot Page"/>

### 4. Bot Permissions

In the Bot page, Scroll down and find **Bot Permissions**

Click the Administrator Box, so it looks as shown:
<img src="https://github.com/Nanosplitter/CompsciBot/imgs/botPerms.png" alt="Bot Permissions"/>

### 4. Config File

Now go to your IDE or Text Editor, and make a copy of `config template.yaml`. Save the copy as `config.yaml`.  This will be the bots config file, and is important to running on discord.

DO NOT WRITE ON THE TEMPLATE

<img src="https://github.com/Nanosplitter/CompsciBot/blob/dev/readme/imgs/configTemplate.png" alt="Template"/>

On the `config.yaml` file, you will be changing four lines:
 
 - `bot_prefix`
 - `token`
 - `application_id`
 - `owner_id`

 `token` and `application_id` you have seen earlier <a href="#token">Here</a> and <a href="#appId">Here</a>  on the Developer Portal.  Copy and Paste those into the quotations to replace BOT_TOKEN and APPLICATION_ID.

 `bot-prefix` is any character that you want to start your commands with.  Avoid **"!"** as that is what the Official CompSci bot uses.

**Generally, avoid using a character another bot uses, as it will call both bots.**

`owner_id` is a bit trickier.

- If you DO NOT have Discord Developer Mode enabled, go to Settings>Advanced, and enable Developer Mode

- If you have Discord Developer Mode turned ON, right click on Settings, and click on the dots next to your name.

If you get stuck on this step, [here is a good reference to help](https://www.alphr.com/discord-find-user-id/).


When you are done getting all of these filled in, your config should be ready to use.

### 5. Create an Invite Link

Back in the Developer Portal, go to **OAuth2 > URL Generator** and check the `[ ] bot` checkbox.  This will show a second set of options called **Bot Permissions**

In bot permissions, check the `[ ] Administrator` checkbox and scroll to the bottom to get an invite link.

The result should look like this below:
<img src="https://github.com/Nanosplitter/CompsciBot/blob/dev/readme/imgs/OAuthChecked.png" alt="Completed OAuth2"/>

### 6. Join the Testing Server and Add the bot.

First, join the **[Compsci Bot Testing Server](https://discord.gg/M48HYYYCyT)** if you havent already. 

Then paste the **Invite Link** you made in step 5. in #general.

If you are just joining, you may not have the permissions to add your bot to the server.  Ask a developer or @Nanosplitter or @chiara5576 and we will give permissions and add your bot. 

Now it should show on the server side panel, but it is not shown as being on.

<img src="https://github.com/Nanosplitter/CompsciBot/blob/dev/readme/imgs/inactive.png" alt="inactive bot"/>

### 7. Running your bot

You are almost done!  Now for the coding part.

First, we will need to install all of the dependencies in the `requirements.txt` file.
Go into the file location of requirements.txt on a terminal, and type:
```
 pip install -r requirements.txt
 ```

It will download all of the dependencies needed for this bot.

Note: the requirements.txt may not download everything.  If it misses something, `pip install <module>` directly, or ask for help in the server for a direct link.

Once installed, to run your bot, simply type:

```
python bot.py
```

This will run your bot!

<img src="https://github.com/Nanosplitter/CompsciBot/blob/dev/readme/imgs/running.png" alt="running command line"/>

You will now see your bot in the ONLINE category, and if you call it with a `<prefix> ping` command it will respond. 




<img src="https://github.com/Nanosplitter/CompsciBot/blob/dev/readme/imgs/ping.png" alt="ping response"/>

press Ctrl+C to stop the bot from running, and now you can work on and change the bot as needed!
