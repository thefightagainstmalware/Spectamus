import tarfile, base64, os, asyncio, aiodocker, tempfile, aiohttp


async def get_file(container: aiodocker.docker.DockerContainer, path: str):
    file_json = await container.get_archive(path)
    text = file_json.extractfile("mitmproxyout")
    q = text.read()
    return q


async def copy_to_container(
    container: aiodocker.docker.DockerContainer, src: str, dst_dir: str
):
    """src shall be an absolute path"""
    stream = tempfile.TemporaryFile()
    with tarfile.open(fileobj=stream, mode="w|") as tar, open(src, "rb") as f:
        info = tar.gettarinfo(fileobj=f)
        info.name = "toanalyze.jar"
        tar.addfile(info, f)
    stream.seek(0)
    await container.put_archive(dst_dir, stream)
    stream.close()


async def run_headlessforge(jarfile):
    aiodocker_client = aiodocker.Docker(
        api_version="v1.41"
    )  # ensure that the api is the same as the one when this program was written
    name = base64.b32encode(os.urandom(32)).decode().strip("=")
    mitmproxy = await aiodocker_client.containers.run(
        {
            "Hostname": None,
            "Domainname": None,
            "ExposedPorts": None,
            "User": None,
            "Tty": False,
            "OpenStdin": False,
            "StdinOnce": False,
            "AttachStdin": False,
            "AttachStdout": False,
            "AttachStderr": False,
            "Env": None,
            "Cmd": None,
            "Image": "tfam/mitm",
            "Volumes": None,
            "NetworkDisabled": False,
            "Entrypoint": None,
            "WorkingDir": None,
            "HostConfig": {"NetworkMode": "mitm", "CapAdd": ["NET_ADMIN"]},
            "NetworkingConfig": {"mitm": None},
            "MacAddress": None,
            "Labels": None,
            "StopSignal": None,
            "Healthcheck": None,
            "StopTimeout": None,
            "Runtime": None,
        },
        name=name,
    )
    headlessforge = await aiodocker_client.containers.run(
        {
            "Hostname": None,
            "Domainname": None,
            "ExposedPorts": None,
            "User": None,
            "Tty": False,
            "OpenStdin": False,
            "StdinOnce": False,
            "AttachStdin": False,
            "AttachStdout": False,
            "AttachStderr": False,
            "Env": ["MITMNAME=" + name],
            "Cmd": None,
            "Image": "tfam/headlessforge",
            "Volumes": None,
            "NetworkDisabled": False,
            "Entrypoint": None,
            "WorkingDir": None,
            "HostConfig": {
                "NetworkMode": "mitm",
                "CapAdd": ["NET_ADMIN"],
                "Dns": ["1.1.1.1", "1.0.0.1"],
            },
            "NetworkingConfig": {"mitm": None},
            "MacAddress": None,
            "Labels": None,
            "StopSignal": None,
            "Healthcheck": None,
            "StopTimeout": None,
            "Runtime": None,
        }
    )
    await copy_to_container(headlessforge, jarfile, "/home/runner/")
    for _ in range(300):
        await asyncio.sleep(1)
        container_data = await headlessforge.show()
        if container_data["State"]["Status"] == "exited":
            break

    container_data = await headlessforge.show()
    if not container_data["State"]["Status"] == "exited":
        print("Container did not exit in time")
        await headlessforge.kill()
    await mitmproxy.kill()
    connector = aiohttp.UnixConnector("/var/run/docker.sock")
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.request(
            method="GET",
            url="unix://localhost/v1.41/containers/" + headlessforge.id + "/logs",
            params={"stdout": "1", "stderr": "1"},
        ) as resp:
            h_logs = await resp.read()
        async with session.request(
            method="GET",
            url="unix://localhost/v1.41/containers/" + mitmproxy.id + "/logs",
            params={"stdout": "1", "stderr": "1"},
        ) as resp:
            m_logs = await resp.read()
    await connector.close()
    return await get_file(mitmproxy, "/home/mitmproxy/mitmproxyout"), h_logs, m_logs
