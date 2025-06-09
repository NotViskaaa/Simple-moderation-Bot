import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, Bot
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

#lista utenti mutati
muted_users = {}

@bot.event
async def on_ready():
    print(f"Bot moderazione attivo come {bot.user}")

#Mute
@bot.command()
@has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: int = None):
    """Mute un utente (opzionale: durata in secondi)"""
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, speak=False, send_messages=False)
    await member.add_roles(mute_role)
    await ctx.send(f"{member.mention} è stato mutato.")
    if duration:
        muted_users[member.id] = ctx.guild.id
        await asyncio.sleep(duration)
        if member.id in muted_users:
            await member.remove_roles(mute_role)
            await ctx.send(f"{member.mention} non è più mutato.")
            muted_users.pop(member.id, None)

#Unmute
@bot.command()
@has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    """Unmute un utente"""
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if mute_role in member.roles:
        await member.remove_roles(mute_role)
        await ctx.send(f"{member.mention} non è più mutato.")
        muted_users.pop(member.id, None)
    else:
        await ctx.send("L'utente non è mutato.")

#checkmute
@bot.command()
async def checkmute(ctx, member: discord.Member):
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if mute_role in member.roles:
        await ctx.send(f"{member.mention} è mutato.")
    else:
        await ctx.send(f"{member.mention} non è mutato.")

#Ban
@bot.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} è stato bannato. Motivo: {reason}")

#Unban
@bot.command()
@has_permissions(ban_members=True)
async def unban(ctx, user: discord.User):
    banned_users = await ctx.guild.bans()
    for ban_entry in banned_users:
        if ban_entry.user.id == user.id:
            await ctx.guild.unban(user)
            await ctx.send(f"{user.mention} è stato sbannato.")
            return
    await ctx.send("Utente non trovato nella lista ban.")

#Checkban
@bot.command()
@has_permissions(ban_members=True)
async def checkban(ctx, user: discord.User):
    banned_users = await ctx.guild.bans()
    if any(ban_entry.user.id == user.id for ban_entry in banned_users):
        await ctx.send(f"{user.mention} è bannato.")
    else:
        await ctx.send(f"{user.mention} non è bannato.")

#Warn
@bot.command()
@has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    await ctx.send(f"{member.mention} è stato avvisato. Motivo: {reason}")

#Purge
@bot.command()
@has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"Ho eliminato {amount} messaggi.", delete_after=3)

#gestione permessi
@mute.error
@unmute.error
@ban.error
@unban.error
@purge.error
@warn.error
async def perm_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("Non hai i permessi per usare questo comando.")

#Crediti
@bot.command()
async def credits(ctx):
    await ctx.send("Bot di moderazione creato da NotVskbi & Ai💕")

#run bot
bot.run("il tuo token")
