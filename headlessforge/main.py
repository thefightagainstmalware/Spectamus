#!/usr/bin/env python3
"""
This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""
import json, subprocess, random, os, os.path, time, platform, uuid, base64

"""
[Get string of all libraries to add to java classpath]
"""


def get_sep():
    return ";" if platform.system() == "Windows" else ":"


def generate_token():
    token = "eyJhbGciOiJIUzI1NiJ9."
    middlePart = f'{{"xuid":"{random.randint(25000000000000, 26000000000000)}", "agg":"Adult", "sub":"{str(uuid.uuid4()).replace("-", "")}", "nbf":"{int(time.time() * 1000)}", "auth":"XBOX", "roles":[], "iss":"authentication", "iat":"{int(time.time() * 1000)}", "platform":"UNKNOWN", "yuid":"{str(uuid.uuid4()).replace("-", "")}"}}'
    middlePart = base64.b64encode(middlePart.encode()).decode().strip("=")
    token += middlePart
    token += "." + "".join(
        [
            random.choice(
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz_"
            )
            for _ in range(43)
        ]
    )
    return token


os.makedirs("./libraries", exist_ok=True)
os.makedirs("./natives", exist_ok=True)
os.makedirs("./.minecraft", exist_ok=True)
os.makedirs("./.minecraft/coremods", exist_ok=True)
os.makedirs("./.minecraft/mods", exist_ok=True)
os.makedirs("./.minecraft/saves", exist_ok=True)
os.makedirs("./.minecraft/screenshots", exist_ok=True)
os.makedirs("./.minecraft/texturepacks", exist_ok=True)
os.makedirs("./.minecraft/config", exist_ok=True)

version = "1.8.9"
username = random.choice(open("usernames.txt").read().splitlines())
uid = uuid.uuid4()
accessToken = generate_token()

mcDir = os.path.join(".", ".minecraft")
nativesDir = os.sep.join([".", "natives"])
clientJson = json.loads(open("resources/1.8.9.json").read())
classPath = get_sep().join(
    [os.path.abspath(os.path.join("./libraries", i)) for i in os.listdir("./libraries")]
)
versionType = clientJson["type"]
assetIndex = clientJson["assetIndex"]["id"]

subprocess.call(
    [
        os.path.join(os.environ["JAVA_HOME"], "bin", "java"),
        f"-Djava.library.path={nativesDir}",
        "-Dminecraft.launcher.version=2.1",
        "-cp",
        classPath,
        "net.minecraft.launchwrapper.Launch",
        "--username",
        username,
        "--version",
        version,
        "--gameDir",
        mcDir,
        "--assetsDir",
        os.path.join(mcDir, "assets"),
        "--assetIndex",
        assetIndex,
        "--uuid",
        str(uid),
        "--accessToken",
        accessToken,
        "--userType",
        "mojang",
        "--versionType",
        "release",
        "--tweakClass",
        "net.minecraftforge.fml.common.launcher.FMLTweaker",
    ]
)
