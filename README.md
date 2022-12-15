# Spectamus
Spectamus (latin, roughly: we are watching) runs suspicious Minecraft mods with Docker and Xvfb to fake a window server.<br>
An instance is running with id: 1020734729554759750 and [this invite url](https://discord.com/api/oauth2/authorize?client_id=1020734729554759750&permissions=8&scope=bot%20applications.commands)
## Running locally
You need 
- [Docker](https://docs.docker.com/get-docker/)
- Python >= 3.8
- 1.8.9 Minecraft json
- Proper .mitmproxy folder
- Requirements.txt dependencies

1. To get a .mitmproxy folder, run [mitmproxy](https://mitmproxy.org) once and copy the .mitmproxy into the mitmproxy directory.<br>
2. Copy the mitmproxy-ca-cert.pem file from the .mitmproxy into the headlessforge directory.<br>
3. Find the 1.8.9 minecraft json and move it to ./headlessforge/resources/1.8.9.json
4. Create a Docker network called `mitm`.<br>
If you get problems with DNS not resolving within a Spectamus container, change the ip in headlessforge/main.sh to the default gateway of the `mitm` network<br>
5. Build lwjgl for your platform and put the so file in a file called `natives-<arch as returned by platform.machine()>`
6. Modify the Dockerfile for the headlessforge directory to change the arch
7. Build the container in the ./headlessforge directory and name it `tfam/headlessmc`<br>
8. Build the container in the ./mitm directory and name it `tfam/mitm`<br>
9. Create a venv, and install all the dependencies in requirements.txt
10. Fill your .env file with the proper data
```env
BOT_TOKEN=<discord bot token, get it at discord.com/developers>
VPN_ASN=<optional, enforces that a you are connected to the VPN by checking the ASN>
LOGGING_CHANNEL_ID=<optional, logs the jars to prevent abuse, put the channel id>
```
11. Run the bot with `python bot.py`
