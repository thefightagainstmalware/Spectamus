from dotenv import load_dotenv
import os, aiohttp, asyncio, discord, lib, tempfile, io, aiosqlite, importlib, ipwhois, interfaces, yarl, socket, ipsafe
from discord.ext import commands
from typing import Optional

class FileTooBig(Exception):
    pass

async def require_vpn(asn: str) -> None:
    """This function is NOT async safe and it IS blocking. Care must be taken when used to not block the main thread"""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://checkip.amazonaws.com") as resp:
            ip = (await resp.text()).strip()
            ourasn = ipwhois.IPWhois(ip).lookup_rdap()["asn"]
            if ourasn != asn.strip("AS"):
                print(f"VPN check failed, Required: {asn}, Actual: {ourasn}")
                exit(1)

async def download(path: str, url: str):
    chunks_written = 0
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            with open(path, 'wb') as fd:
                async for chunk in resp.content.iter_chunked(16 * 1024):
                    if chunks_written == 1920:
                        raise FileTooBig()
                    fd.write(chunk)
                    chunks_written += 1
                    
def validate_url(url: str) -> bool:
    url_obj = yarl.URL(url) # use yarl because aiohttp uses yarl, make sure aiohttp and us parse the url the same way
                            # which prevents an attacks where we think the url is safe but aiohttp makes a request to an unsafe destination
    addrinfo = socket.getaddrinfo(url_obj.host, url_obj.port)
    for address in addrinfo:
        if not ipsafe.check_ip(address[4][0]):
            return False
    return True
        

async def check_owner(ctx: interfaces.FailMessagedContext):
    is_owner = await client.is_owner(ctx.author)
    if not is_owner:
        ctx.fail_message = "You are not the owner of this bot!"
    return is_owner

def str_to_discord_file(data: str, filename: str):
    return discord.File(io.StringIO(data), filename=filename)


def bytes_to_discord_file(data: bytes, filename: str):
    return discord.File(io.BytesIO(data), filename=filename)


load_dotenv()

if os.getenv("VPN_ASN") is not None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(require_vpn(os.getenv("VPN_ASN")))


client = discord.Bot(intents=discord.Intents.default())


@client.check_once
async def check_banned(ctx: discord.ApplicationContext):
    db = await aiosqlite.connect("bot.db")
    banned = await (
        await db.execute("SELECT * FROM bans WHERE id=?", (ctx.author.id,))
    ).fetchone()
    if banned is not None:
        ctx.fail_message = f"You are banned from using this bot. Reason: {banned[1]}"
    return banned is None

@client.event
async def on_application_command_error(
    ctx: interfaces.FailMessagedContext, error: discord.DiscordException
):
    if isinstance(error, discord.errors.CheckFailure):
        await ctx.respond(
            ctx.fail_message
        )
        return
    raise error
  
@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))
    con = await aiosqlite.connect("bot.db")
    await con.execute(
        "CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, mitmproxy_file TEXT, mitmproxy_logs TEXT, headlessforge_logs TEXT, user_id INTEGER)"
    )
    await con.execute(
        "CREATE TABLE IF NOT EXISTS bans (id INTEGER PRIMARY KEY, reason TEXT)"
    )
    await con.execute(
        "CREATE TABLE IF NOT EXISTS primaryKeys (key INTEGER PRIMARY KEY)"
    )
    await con.commit()
    await con.close()


@client.slash_command(debug_guilds=[910733698452815912])
@commands.check(check_owner)
async def reload(ctx: discord.ApplicationContext):
    importlib.reload(lib)
    await ctx.respond("Reloaded lib.py")


@client.slash_command(debug_guilds=[910733698452815912])
async def run_headlessforge(ctx: discord.ApplicationContext, file: Optional[discord.Attachment], url: Optional[str]):
    """Runs HeadlessForge using Spectamus"""
    await ctx.defer()
    db = await aiosqlite.connect("bot.db")
    
    fp = tempfile.NamedTemporaryFile()
    if file != None:
        if file.size > 1024 * 1024 * 30:
            await ctx.respond("C'mon, even NEU is not that big")
            return
        await file.save(fp.name)
    elif url != None:
        loop = asyncio.get_event_loop()
        safe = await loop.run_in_executor(None, validate_url, url)
        if not safe:
            await ctx.respond("The URL seems to be malicious...\nThis detection can be wrong. If so, contact the developers")
            return
        try:
            await download(fp.name, url)
        except FileTooBig:
            await ctx.respond("C'mon, even NEU is not that big")
            return
    else:
        await ctx.respond("You must send me a file or a URL!")
        return
    row = await db.execute("SELECT max(key) FROM primaryKeys")
    primary_key = (await row.fetchone())[0]
    if primary_key is None:
        primary_key = 0
    await db.execute("INSERT INTO primaryKeys VALUES (?)", (primary_key + 1,))
    await db.commit()
    await ctx.respond(
        "HeadlessForge is running! Check back soon (max 5 minutes) with key: "
        + hex(int(primary_key))[2:]
    )
    mitmproxy, h_logs, m_logs = await lib.run_headlessforge(fp.name)
    if not isinstance(mitmproxy, str):
        mitmproxy = mitmproxy.read()

    h_logs, m_logs = h_logs.read().decode("utf-8"), m_logs.read().decode("utf-8")
    await db.execute(
        "INSERT INTO results (id, mitmproxy_file, mitmproxy_logs, headlessforge_logs, user_id) VALUES (?, ?, ?, ?, ?)",
        (primary_key, mitmproxy, h_logs, m_logs, ctx.author.id),
    )
    await db.commit()
    await db.close()
    if os.getenv("LOGGING_CHANNEL_ID"):
        fp.seek(0)
        if isinstance(mitmproxy, str):
            await client.get_channel(int(os.getenv("LOGGING_CHANNEL_ID"))).send(
                f"HeadlessForge run by {ctx.author.mention}, id: {ctx.author.id}, mitmproxy output {mitmproxy}",
                files=[
                    discord.File(fp.name, "toanalyze.jar"),
                    str_to_discord_file(m_logs, "mitmproxy.log"),
                    str_to_discord_file(h_logs, "headlessforge.log"),
                ],
            )
        else:
            await client.get_channel(int(os.getenv("LOGGING_CHANNEL_ID"))).send(
                f"HeadlessForge run by {ctx.author.mention}, id: {ctx.author.id}",
                files=[
                    discord.File(fp.name, "toanalyze.jar"),
                    bytes_to_discord_file(mitmproxy, "mitmproxy.out"),
                    str_to_discord_file(m_logs, "mitmproxy.log"),
                    str_to_discord_file(h_logs, "headlessforge.log"),
                ],
            )

@client.slash_command(debug_guilds=[910733698452815912])
async def get_result(ctx: discord.ApplicationContext, key: str):
    """Get the result of a HeadlessForge run"""
    db = await aiosqlite.connect("bot.db")
    ikey = int(key, 16)
    result = await db.execute("SELECT * FROM results WHERE id=?", (ikey,))
    data = await result.fetchone()
    if data is None:
        await ctx.respond("No result found with key: " + key)
        return
    _, mitmproxy_file, mitmproxy_logs, headlessforge_logs, user_id = data
    if ctx.author.id != user_id:
        await ctx.respond("You are not the owner of this result! ")
        return
    await db.close()
    if isinstance(mitmproxy_file, str):
        await ctx.respond(
            f"HeadlessForge results: mitmproxy output: {mitmproxy_file}",
            files=[
                str_to_discord_file(mitmproxy_logs, "mitmproxy.log"),
                str_to_discord_file(headlessforge_logs, "headlessforge.log"),
            ],
        )
    else:
        await ctx.respond(
            f"HeadlessForge results:",
            files=[
                bytes_to_discord_file(mitmproxy_file, "mitmproxy.out"),
                str_to_discord_file(mitmproxy_logs, "mitmproxy.log"),
                str_to_discord_file(headlessforge_logs, "headlessforge.log"),
            ],
        )


@client.slash_command(debug_guilds=[910733698452815912])
@commands.check(check_owner)
async def ban(ctx: discord.ApplicationContext, user: discord.User, reason: str):
    """Cheaters get banned"""
    db = await aiosqlite.connect("bot.db")
    await db.execute("INSERT INTO bans (id, reason) VALUES (?, ?)", (user.id, reason))
    await db.commit()
    await db.close()
    await ctx.respond(f"Banned {user.mention} for {reason}")


@client.slash_command(debug_guilds=[910733698452815912])
@commands.check(check_owner)
async def unban(ctx: discord.ApplicationContext, user: discord.User):
    """Appeals actually working??????"""
    db = await aiosqlite.connect("bot.db")
    await db.execute("DELETE FROM bans WHERE id=?", (user.id,))
    await db.commit()
    await db.close()
    await ctx.respond(f"Unbanned {user.mention}")


@client.slash_command(debug_guilds=[910733698452815912])
@commands.check(check_owner)
async def purge(ctx: discord.ApplicationContext):
    """Purges docker containers"""
    await ctx.defer()
    proc = await asyncio.subprocess.create_subprocess_exec(
        "docker",
        "container",
        "prune",
        "-f",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    await ctx.respond(
        f"Docker purge results:",
        files=[
            str_to_discord_file(
                (stdout or b"").decode() + (stderr or b"").decode(), "purge-log.txt"
            )
        ],
    )


client.run(os.getenv("BOT_TOKEN"))
