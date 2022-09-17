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
Add your compiled HeadlessForge jar into the headlessforge directory also<br>
Create a network called `mitm`<br>
If you get problems with DNS not resolving within a headlessforge container, change the ip in headlessforge/main.sh to the default gateway of the `mitm` network
Build the container in the ./headlessforge directory and name it `tfam/headlessforge`
Build the container in the ./mitm directory and name it `tfam/mitm`
