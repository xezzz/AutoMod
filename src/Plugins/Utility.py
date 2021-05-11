import os
import asyncio
import time
import traceback
import argparse
import shlex
from datetime import datetime

import discord
from discord.ext import commands

from i18n import Translator
from Utils import Logging, Utils, guild_info
from Utils.Converters import DiscordUser, Guild

from Database import Connector, DBUtils
from Plugins.Base import BasePlugin


db = Connector.Database()


class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


class Utility(BasePlugin):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def jumbo(self, ctx, emoji: discord.Emoji):
        """jumbo_help"""
        await ctx.send(f"{emoji.url}")


    @commands.command(aliases=["info"])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(embed_links=True)
    async def userinfo(self, ctx, user: DiscordUser = None):
        """userinfo_help"""
        try:
            if user is None:
                user = member = ctx.author
            else:
                member = None if ctx.guild is None else await Utils.get_member(self.bot, ctx.guild, user.id)
            
            e = discord.Embed(color=self.bot.color)
            e.set_thumbnail(url=user.avatar_url)

            created = user.created_at.strftime("%d/%m/%Y")
            e.add_field(
                name="User Information",
                value="```\n• ID: {} \n• Name: {}#{} \n• Created: {} \n```"\
                .format(
                    user.id, user.name, user.discriminator, 
                    f"{(datetime.fromtimestamp(time.time()) - user.created_at).days} days ago ({created})"
                ),
                inline=False
            )

            if member is not None:
                try:
                    roles = [r.name for r in reversed(member.roles) if r != ctx.guild.default_role]
                except Exception:
                    roles = ["No roles"]
                
                joined = member.joined_at.strftime("%d/%m/%Y")
                e.add_field(
                    name="Member Information",
                    value="```\n• Joined: {} \n• Roles: {} \n```"\
                    .format(
                        f"{(datetime.fromtimestamp(time.time()) - member.joined_at).days} days ago ({joined})", 
                        f"{', '.join(roles) if len(roles) < 20 else f'{len(roles)} roles'}"
                    ),
                    inline=False
                )

            warns = len([x for x in db.warns.find() if str(x["warnId"].split("-")[1]) == str(member.id)])
            e.add_field(
                name="Infractions", 
                value="```\n• Total cases: {} \n```".format(warns if warns >= 1 else "0"),
                inline=False
            )

            await ctx.send(embed=e)
        except Exception:
            ex = traceback.format_exc()
            print(ex)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def server(self, ctx, guild: Guild = None):
        """server_help"""
        if guild is None:
            guild = ctx.guild
        e = guild_info.guild_info_embed(guild)
        await ctx.send(embed=e)
        

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def avatar(self, ctx, user: DiscordUser = None):
        """avatar_help"""
        if user is None:
            user = ctx.author
        e = discord.Embed(
            color=self.bot.color,
            title="{}'s Avatar".format(user.name)
        )
        e.set_image(
            url=user.avatar_url
        )
        await ctx.send(embed=e)


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def cleanup(self, ctx, search=100):
        """cleanup_help"""
        strategy = Utils.basic_cleaning
        if ctx.me.permissions_in(ctx.channel).manage_messages:
            strategy = Utils.complex_cleaning
        
        deleted = await strategy(ctx, search)
        await ctx.send(Translator.translate(ctx.guild, "clean_success", _emote="YES", deleted=deleted, plural="" if deleted == 1 else "s"))
        

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def post(self, ctx, channel: discord.TextChannel, *, content):
        """post_help"""
        if len(content) < 1:
            return await ctx.send(Translator.translate(ctx.guild, "min_content", _emote="WARN"))
        if len(content) > 2000:
            return await ctx.send(Translator.translate(ctx.guild, "max_content", _emote="WARN"))
        
        try:
            await channel.send(content=content)
            await ctx.send(Translator.translate(ctx.guild, "message_posted", _emote="YES"))
        except Exception as ex:
            await ctx.send(Translator.translate(ctx.guild, "posting_failed", _emote="WARN", exc=ex))

    
    @commands.command(usage="post_embed <channel> [-content] [-title] [-color]")
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def post_embed(self, ctx, channel: discord.TextChannel, *, args):
        """post_embed_help"""
        p = Arguments(add_help=False, allow_abbrev=False)

        p.add_argument("-content", nargs="+")
        p.add_argument("-title", nargs="+")
        p.add_argument("-color", type=int)

        try:
            args = p.parse_args(shlex.split(args))
        except Exception as ex:
            return await ctx.send(str(ex))
        
        content = " ".join(args.content) if args.content else ""
        if len(content) < 1:
            return await ctx.send(Translator.translate(ctx.guild, "min_content"))
        if len(content) > 2000:
            return await ctx.send(Translator.translate(ctx.guild, "max_content"))
        e = discord.Embed(
            color=args.color if args.color else self.bot.color, 
            title=" ".join(args.title) if args.title else None,
            description=content
        )

        try:
            await channel.send(embed=e)
            await ctx.send(Translator.translate(ctx.guild, "message_posted", _emote="YES"))
        except Exception as ex:
            await ctx.send(Translator.translate(ctx.guild, "posting_failed", _emote="WARN", exc=ex))
        





def setup(bot):
    bot.add_cog(Utility(bot))