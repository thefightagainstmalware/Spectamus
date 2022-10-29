import aiodocker, tempfile, aiohttp, typing, asyncio, struct

async def get_archive(
    container: aiodocker.docker.DockerContainer, path: str
) -> tempfile.TemporaryFile:
    """get a file from a container, streaming it so the memory doesn't run out

    Args:
        container (aiodocker.docker.DockerContainer): the container to get the data from
        path (str): the filepath of the file to get

    Returns:
        tempfile.TemporaryFile: the tempfile that has the tarfile of the file
    """
    file = tempfile.TemporaryFile()
    async with aiohttp.UnixConnector("/var/run/docker.sock") as uc:
        async with aiohttp.ClientSession(connector=uc) as session:
            async with session.get(
                f"unix://localhost/v1.41/containers/{container.id}/archive",
                params={"path": path},
            ) as resp:
                async for content in resp.content.iter_chunked(16384):  # 16 Kib
                    file.write(content)
    file.seek(0)
    return file

async def unpack(resp: aiohttp.ClientResponse, temp_file: typing.IO[bytes]):
    while True:
        try:
            await resp.content.readexactly(4) # discard the indicator, and the 3 null bytes, we don't care about them
            size = struct.unpack(">I", await resp.content.readexactly(4))[0]
            temp_file.write(await resp.content.readexactly(size))
        except asyncio.IncompleteReadError:
            break
    