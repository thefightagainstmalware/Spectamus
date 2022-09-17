# Spectamus
Spectamus (latin, roughly: we are watching) runs suspicious Minecraft mods with HeadlessForge
## Running locally
You need 
- [Docker](https://docs.docker.com/get-docker/)
- Python >= 3.7
- [HeadlessForge jar built](https://github.com/thefightagainstmalware/HeadlessForge)
- Proper .mitmproxy folder
- Requirements.txt dependencies

To get a .mitmproxy folder, run [mitmproxy](https://mitmproxy.org) once and copy the .mitmproxy into the mitmproxy directory<br>
Copy the mitmproxy-ca-cert.pem file from the .mitmproxy to the headlessforge directory<br>
Add your compiled HeadlessForge jar into the headlessforge directory also
