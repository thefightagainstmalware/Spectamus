#!/usr/bin/env python3
"""
This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""
import tarfile, json, subprocess, random, os, os.path, time, platform, uuid, requests, base64, shutil, functools


def save_to_file(url: str, folder="libraries") -> str:
    r = requests.get(url, stream=True)
    r.raw.read = functools.partial(r.raw.read, decode_content=True)
    if folder == None:
        with open(url.split("/")[-1], "wb") as f:
            shutil.copyfileobj(r.raw, f)
        return url.split("/")[-1]
    else:
        with open(os.path.join(folder, url.split("/")[-1]), "wb") as f:
            shutil.copyfileobj(r.raw, f)
        return os.path.join(".", folder, url.split("/")[-1])


"""
Debug output
"""


def debug(str):
    if os.getenv("DEBUG") != None:
        print(str)


"""
[Parses "rule" subpropery of library object, testing to see if should be included]
"""


def should_use_library(lib):
    def rule_says_yes(rule):
        useLib = None

        if rule["action"] == "allow":
            useLib = False
        elif rule["action"] == "disallow":
            useLib = True

        if "os" in rule:
            for key, value in rule["os"].items():
                os = platform.system()
                if key == "name":
                    if value == "windows" and os != "Windows":
                        return useLib
                    elif value == "osx" and os != "Darwin":
                        return useLib
                    elif value == "linux" and os != "Linux":
                        return useLib
                elif key == "arch":
                    if value == "x86" and platform.architecture()[0] != "32bit":
                        return platform.machine() == "AMD64"

        return not useLib

    if (
        "serverreq" in lib
        and lib["serverreq"] == True
        and "clientreq" in lib
        and lib["clientreq"] == False
    ):
        return False
    if not "rules" in lib:
        return True

    for i in lib["rules"]:
        if rule_says_yes(i):
            return True

    return False


def mavenify(url: str, name: str):
    if name == "net.minecraftforge:forge:1.8.9-11.15.1.2318-1.8.9:universal":
        return "https://files.minecraftforge.net/maven/net/minecraftforge/forge/1.8.9-11.15.1.2318-1.8.9/forge-1.8.9-11.15.1.2318-1.8.9-universal.jar"
    version = name.split(":")[-1]
    artifact = name.split(":")[-2]
    package = name.split(":")[0]
    return f"{url}{package.replace('.', '/')}/{artifact}/{version}/{artifact}-{version}.jar"


"""
[Get string of all libraries to add to java classpath]
"""


def get_classpath(lib):
    cp = set()
    if "downloads" in lib:
        cp.add(os.path.abspath(save_to_file(lib["downloads"]["client"]["url"])))
    for i in lib["libraries"]:
        if not should_use_library(i):
            continue
        try:
            if "downloads" in i and "artifact" in i["downloads"]:
                cp.add(os.path.abspath(save_to_file(i["downloads"]["artifact"]["url"])))
            elif "url" in i:
                cp.add(os.path.abspath(save_to_file(mavenify(i["url"], i["name"]))))
            else:
                cp.add(
                    os.path.abspath(
                        save_to_file(
                            mavenify("https://libraries.minecraft.net/", i["name"])
                        )
                    )
                )

        except KeyError as ke:
            print("KeyError: " + str(i))
            print(ke)

    return cp

def extract_natives():
    if os.path.exists(f"natives-{platform.machine()}.tar"):
        file = tarfile.open(f"natives-{platform.machine()}.tar")
        file.extractall("natives")
        file.close()
        return
    raise Exception(
        f"natives-{platform.machine()}.tar doesn't exist, most likely because it hasn't been built for this architecture, please build it yourself"
    )


os.makedirs("./libraries", exist_ok=True)
os.makedirs("./natives", exist_ok=True)
extract_natives()
clientJson = json.loads(open("./resources/1.8.9.json").read())
classPath = get_classpath(clientJson)
classPath.union(get_classpath(json.loads(open("resources/forge.json").read())))