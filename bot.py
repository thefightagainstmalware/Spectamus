from dotenv import load_dotenv
import os, aiohttp, asyncio, discord, typing, lib, tempfile, io, aiosqlite


async def require_vpn(asn) -> "typing.Union[typing.NoReturn, None]":
    async with aiohttp.ClientSession() as session:
        async with session.get("https://ipinfo.io/json") as resp:
            data = await resp.json()
            if data["org"].split(" ")[0] != asn:
                print("Not connected to VPN")
                os._exit(1)


def bytes_to_file(data: bytes, filename: str):
    buf = io.BytesIO(data)
    return discord.File(buf, filename=filename)


load_dotenv()

if os.getenv("VPN_ASN") is not None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(require_vpn(os.getenv("VPN_ASN")))


client = discord.Bot()


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
    await con.commit()
    await con.close()


@client.slash_command(debug_guilds=[910733698452815912])
async def run_headlessforge(ctx: discord.ApplicationContext, file: discord.Attachment):
    """Runs HeadlessForge using Spectamus"""
    db = await aiosqlite.connect("bot.db")
    banned = await (
        await db.execute("SELECT * FROM bans WHERE id=?", (ctx.author.id,))
    ).fetchone()
    if banned is not None:
        await ctx.respond(
            "You are banned from using this bot. Reason: {}".format(banned[1])
        )
        return
    if file.size > 1024 * 1024 * 30:
        await ctx.respond("C'mon, even NEU is not that big")
        return
    fp = tempfile.NamedTemporaryFile()
    await file.save(fp.name)
    row = await db.execute("SELECT max(id) FROM results")
    primary_key = (await row.fetchone())[0]
    if primary_key is None:
        primary_key = 1
    await ctx.respond(
        "HeadlessForge is running! Check back soon (max 5 minutes) with key: "
        + hex(int(primary_key))[2:]
    )
    mitmproxy, h_logs, m_logs = await lib.run_headlessforge(fp.name)
    await db.execute(
        "INSERT INTO results (mitmproxy_file, mitmproxy_logs, headlessforge_logs, user_id) VALUES (?, ?, ?, ?)",
        (mitmproxy, h_logs, m_logs, ctx.author.id),
    )
    await db.commit()
    await db.close()
    if os.getenv("LOGGING_CHANNEL_ID"):
        fp.seek(0)
        await client.get_channel(int(os.getenv("LOGGING_CHANNEL_ID"))).send(
            f"HeadlessForge run by {ctx.author.mention}, id: {ctx.author.id}",
            files=[
                discord.File(fp.name, "toanalyze.jar"),
                bytes_to_file(m_logs, "mitmproxy.log"),
                bytes_to_file(h_logs, "headlessforge.log"),
                bytes_to_file(mitmproxy, "mitmproxy.out"),
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
    await ctx.respond(
        "HeadlessForge results: ",
        files=[
            bytes_to_file(mitmproxy_file, "mitmproxy.out"),
            bytes_to_file(mitmproxy_logs, "mitmproxy.log"),
            bytes_to_file(headlessforge_logs, "headlessforge.log"),
        ],
    )


@client.slash_command(debug_guilds=[910733698452815912])
async def ban(ctx: discord.ApplicationContext, user: discord.User, reason: str):
    """Cheaters get banned"""
    if not await client.is_owner(ctx.author):
        print(client.owner_ids)
        await ctx.respond("You are not the owner of this bot!")
        return
    db = await aiosqlite.connect("bot.db")
    await db.execute("INSERT INTO bans (id, reason) VALUES (?, ?)", (user.id, reason))
    await db.commit()
    await db.close()
    await ctx.respond(f"Banned {user.mention} for {reason}")


@client.slash_command(debug_guilds=[910733698452815912])
async def unban(ctx: discord.ApplicationContext, user: discord.User):
    """Appeals actually working??????"""
    if not await client.is_owner(ctx.author):
        print(client.owner_ids)
        await ctx.respond("You are not the owner of this bot!")
        return
    db = await aiosqlite.connect("bot.db")
    await db.execute("DELETE FROM bans WHERE id=?", (user.id,))
    await db.commit()
    await db.close()
    await ctx.respond(f"Unbanned {user.mention}")


client.run(os.getenv("BOT_TOKEN"))
