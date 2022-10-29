import tarfile, base64, os, asyncio, aiodocker, tempfile, aiohttp, dockerlib, traceback, io
from typing import Tuple, IO
from interfaces import NamedFile


async def get_file(container: aiodocker.docker.DockerContainer, path: str) -> NamedFile:
    file_json = await dockerlib.get_archive(container, path)
    file = tempfile.NamedTemporaryFile()
    tf = tarfile.open(fileobj=file_json)
    br = tf.extractfile("mitmproxyout")
    while True:
        data = br.read(16384)
        if data == b"":
            break
        file.write(data)
    return file


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


async def upload(filepath: str) -> str:
    proc = await asyncio.create_subprocess_exec(
        "ffsend",
        *[
            "upload",
            "-q",
            "-d",
            "100",
            "-e",
            "365d",
            "--host",
            "https://send.zcyph.cc/",
            "--force",
            filepath,
        ],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    out = (stdout or b"") + (stderr or b"")
    return out.decode("utf-8")


async def run_headlessforge(jarfile: str) -> "Tuple[str, str, str]":
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
    await asyncio.sleep(5) # oh god this hack has got to be the worst
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
            "Image": "tfam/headlessmc",
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
    for _ in range(120):
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
            h_log_file = io.BytesIO()
            await dockerlib.unpack(resp, h_log_file)
        async with session.request(
            method="GET",
            url="unix://localhost/v1.41/containers/" + mitmproxy.id + "/logs",
            params={"stdout": "1", "stderr": "1"},
        ) as resp:
            m_log_file = io.BytesIO()
            await dockerlib.unpack(resp, m_log_file)
    await connector.close()

    try:
        file = await get_file(mitmproxy, "/home/mitmproxy/mitmproxyout") # prevent python from garbage collecting it and then the file goes poof
        m_out = await upload(
            (file).name
        )
    except Exception as e:
        m_out = "Something went wrong..."
        traceback.print_exception(type(e), e, e.__traceback__)

    return m_out, h_log_file.getvalue().decode("utf-8"), m_log_file.getvalue().decode("utf-8")
