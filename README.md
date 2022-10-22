# Spectamus
Spectamus (latin, roughly: we are watching) runs suspicious Minecraft mods with HeadlessForge.<br>
An instance is running with id: 1020734729554759750 and [this invite url](https://discord.com/api/oauth2/authorize?client_id=1020734729554759750&permissions=8&scope=bot%20applications.commands)
## Running locally
You need 
- [Docker](https://docs.docker.com/get-docker/)
- Python >= 3.7
- [HeadlessForge jar built](https://github.com/thefightagainstmalware/HeadlessForge)
- Proper .mitmproxy folder
- Requirements.txt dependencies

1. To get a .mitmproxy folder, run [mitmproxy](https://mitmproxy.org) once and copy the .mitmproxy into the mitmproxy directory.<br>
2. Copy the mitmproxy-ca-cert.pem file from the .mitmproxy into the headlessforge directory.<br>
3. Add your compiled HeadlessForge jar into the headlessforge directory also.<br>
4. Create a Docker network called `mitm`.<br>
If you get problems with DNS not resolving within a headlessforge container, change the ip in headlessforge/main.sh to the default gateway of the `mitm` network<br>
5. Build the container in the ./headlessforge directory and name it `tfam/headlessforge`<br>
6. Build the container in the ./mitm directory and name it `tfam/mitm`<br>
7. Create a venv, and install all the dependencies in requirements.txt
8. Run the bot with `python bot.py`
