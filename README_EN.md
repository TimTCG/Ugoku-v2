<h2>Installation Guide</h2>

>[!NOTE]
> This guide was created before the Deezer feature was developed, please refer to the ```.env.template``` for how to add the Deezer feature to the bot.

<h4>Discord API (Main API, used to bring the bot to life :)) )</h4>

- Go to the Discord developer portal at the following link: <a href="https://discord.com/developers/applications">Discord Developer Portal</a>
- Click the **New Application** button.
<p></p>
<div align = "center">
<img src="img\readme_disdev_dashboard.png" alt="discord developer dashboard"/>
</div>
<p></p>
- Name the application and click <b>Create</b>
<p></p>
<div align = "center">
<img src="img\readme_disdev_createapp.png" alt="discord developer create app"/>
</div>
<p></p>
- On the left sidebar, select Installation and ensure your settings match the image. After editing, click the **Save Changes** button to save the changes. Pay attention to the link in the **Install Link** section, you will use this link to add the bot to your server.
<p></p>
<div align = "center">
<img src="img\readme_disdev_installation.png" alt="discord developer bot installation"/>
</div>
<p></p>
- Next, go to the Bot section in the left sidebar, add, edit the name, avatar, banner for the bot, and click the **Reset Token** button to get the bot token. After the token appears, copy it and paste it into the ```BOT_TOKEN``` field in the .env file
<p></p>
<div align = "center">
<img src="img\readme_disdev_bot.png" alt="discord developer bot information"/>
</div>
<p></p>

>[!NOTE]
>It's important to note that this token is actually your bot's password. You should never share this with anyone because someone could log into your bot and perform harmful actions, such as leaving the server, banning all members inside the server, or maliciously attacking people. If you accidentally leak your token, click the "Regenerate" button as soon as possible. This action revokes your token and creates a new token for login.

<h4>Spotify API (If you want to use Spotify features)</h4>

- Go to the Spotify developer page and log in with your Spotify account **(Must be using Spotify Premium)**: https://developer.spotify.com/dashboard and create an account
- Click the **Create App** button
<p></p>
<div align = "center">
<img src="img\readme_spotdev_dashboard.png" alt="spotify developer dashboard"/>
</div>
<p></p>
- Enter name, description, redirect URL (this can be entered arbitrarily), select the correct SDK type as shown in the image, understand and accept Spotify's terms and click **Save**
<p></p>
<div align = "center">
<img src="img\readme_spotdev_appcreate.png" alt="spotify developer app create screen"/>
</div>
<p></p>
- After successfully creating the application, return to Dashboard, where your application will now appear. Click on it and go to **Settings**
<p></p>
<div align = "center">
<img src="img\readme_spotdev_appmainscreen.png" alt="spotify developer app create screen"/>
</div>
<p></p>
- At the top of the page, click the **View client secret** button
<p></p>
<div align = "center">
<img src="img\readme_spotdev_appsettings.png" alt="spotify developer app create screen"/>
</div>
<p></p>
- Now, copy the Client ID and Client secret lines and save them
<p></p>
<div align = "center">
<img src="img\readme_spotdev_appsettings-1.png" alt="spotify developer app create screen"/>
</div>

<h4>Gemini + Pinecone API (If you want to use AI-related features including chatbot and song lyrics translation)</h4>
- Go to the Google API key creation page here <a href="https://aistudio.google.com/app/u/1/apikey">Google API Studio</a>, click the <b>Create API Key</b> button, select your project, and create an API key.

<p></p>
<div align = "center">
<img src="img\readme_gemini_api.png" alt="gemini api"/>
</div>
<p></p>

>[!NOTE]
>This guide assumes you already have a Google Cloud account and a project to use it. If you don't have one, create a new account <a href="https://console.cloud.google.com/welcome/new">here</a>. Using the Gemini API is charged, check the price form <a href="https://ai.google.dev/pricing">here</a>.

- For Pinecone, sign up or log in to your account, then select **API Keys** in the left sidebar and choose **Create API key** in the top right of the screen

<p></p>
<div align = "center">
<img src="img\readme_pinecone_apimain.png" alt="pinecone api main"/>
</div>
<p></p>

- Enter a name and click **Create key**

<p></p>
<div align = "center">
<img src="img\readme_pinecone_newapi.png" alt="pinecone api create new"/>
</div>
<p></p>

- Copy your API key and paste it into the ```PINECONE_API``` field in the ```.env``` file

>[!NOTE]
>Keep your API key very carefully, as there is no way to retrieve the API key when forgotten and you will have to create a new key

<h4>Imgur API (If you want to use another platform to display album images)</h4>

- Create an Imgur account and register a new application here https://api.imgur.com/oauth2/addclient

- After creating the application, copy the **Client ID** and paste it into ```IMGUR_CLIENT_ID``` in the ```.env``` file

<h3>Download and Run the Bot</h3>

- Download or clone this repository to a folder on your computer
```git
git clone https://github.com/Shewiiii/Ugoku-v2.git
```
- If you're using Python 3.4+, you can create a Python virtual environment in that directory with the following command
```python
python -m venv <Ugoku folder>
```
>[!NOTE]
>If you encounter an error while creating a virtual environment on Python, make sure you have downloaded the virtualenv package first. You can download it with this command ```pip install virtualenv``` and use ```virtualenv <Ugoku folder>``` to create a virtual environment.
- Access your virtual environment
```
# For Windows
# In cmd.exe
<Ugoku folder>\Scripts\activate.bat
# In PowerShell
<Ugoku folder>\Scripts\Activate.ps1
```
```
# In Linux
source <Ugoku folder>/bin/activate
```
- Access the following files to change content to suit your environment:
  - ```.env.template```: Add API values for the bot to function. After adding, rename it to ```.env``` for the system to recognize
  - ```config.py```: Set basic bot values, including turning Spotify, chatbot features on/off
- After completing edits, enter the following command to run the bot
```python
python main.py
```
>[!NOTE]
> When running the bot for the first time, it will ask you to log into Spotify on the server where you are hosting. Connect to the server running the bot through the Spotify app as follows:
> - Open Spotify and play any content.
> - Click the device connection icon at the bottom of the screen.
> - Select the server where you are hosting the bot.
>> From the second run onwards, the bot will use the login information you've provided as its basis for operation.

>[!NOTE]
> When you can't find the server hosting the bot, do the following steps:
> - Depending on your main device version, download or copy the following repository to your computer <a href=https://github.com/dspearson/librespot-auth>Link</a>
> - Download the Rust toolchain (See https://rustup.rs/), and run `cargo build --release`.
> - After completion, run the following command
> ```bash
>$ ./target/release/librespot-auth --name "<name>" --class=speaker
>Follow the connection instructions above and choose "<Name>" as the device you need to connect
>```
>At this point, you will see a file named ```credentials.json``` in the current directory. Open your preferred text editor like Notepad or Notepad++, and edit it according to the following structure:
>```json
>{
>   "username": "your spotify username, default is the first string of letters and numbers",
>   "credentials": "gekiyaba long string",
>   "type": "AUTHENTICATION_STORED_SPOTIFY_CREDENTIALS"
>}
>```
>After editing, copy the file and paste it into the folder containing Ugoku and use the ```python main.py``` command to run it again. If it still requires you to log into Spotify, copy the file and paste it into the ```bot/vocal``` folder and run the bot again.