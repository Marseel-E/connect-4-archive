import discord
from discord.ext import commands


class Lair(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.Cog.listener(name="on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        # Connect 4's lair
        if payload.guild_id == 843994109366501376:
            guild = self.client.get_guild(payload.guild_id)
            # Verification system
            if payload.channel_id == 846981584774103113 and payload.message_id == 847086273993637919:
                    human = guild.get_role(846976407900520489)
                    await payload.member.add_roles(human)
            # Self roles add
            if payload.channel_id == 846985091053649944 and payload.message_id == 847096713949085776:
                python = guild.get_role(846983176143634432)
                javascript = guild.get_role(846983569582719016)
                cs = guild.get_role(846983682790260737)
                if payload.emoji.id == 847092622237499403 and python not in payload.member.roles: await payload.member.add_roles(python)
                if payload.emoji.id == 847093478621053029 and javascript not in payload.member.roles: await payload.member.add_roles(javascript)
                if payload.emoji.id == 847093467029176370 and cs not in payload.member.roles: await payload.member.add_roles(cs)

    @commands.Cog.listener(name="on_raw_reaction_remove")
    async def on_raw_reaction_remove(self, payload):
        # Connect 4's lair
        if payload.guild_id == 843994109366501376:
            guild = self.client.get_guild(payload.guild_id)

            # Self roles remove
            if payload.channel_id == 846985091053649944 and payload.message_id == 847096713949085776:
                python = guild.get_role(846983176143634432)
                javascript = guild.get_role(846983569582719016)
                cs = guild.get_role(846983682790260737)
                news = guild.get_role(857136111524380672)
                giveaways = guild.get_role(857136292419993630)
                events = guild.get_role(857136360116715541)
                tournaments = guild.get_role(857136411752661032)
                member = guild.get_member(payload.user_id)
                if payload.emoji.id == 847092622237499403 and python in member.roles: await member.remove_roles(python)
                if payload.emoji.id == 847093478621053029 and javascript in member.roles: await member.remove_roles(javascript)
                if payload.emoji.id == 847093467029176370 and cs in member.roles: await member.remove_roles(cs)
                if payload.emoji == "🗞️" and news in member.roles: await member.remove_roles(cs)
                if payload.emoji == "🎁" and giveaways in member.roles: await member.remove_roles(cs)
                if payload.emoji == "🎟️" and events in member.roles: await member.remove_roles(cs)
                if payload.emoji == "🏁" and tournaments in member.roles: await member.remove_roles(cs)
    

    # @commands.Cog.listener(name="on_voice_state_update")
    # async def on_voice_state_update(self, member, before, after):
    #     guild = member.guild
    #     if guild.id == 843994109366501376:
    #         channel = before.channel
    #         if (after.channel): channel = after.channel
    #         # Delete personal channel
    #         if channel.name == member.name and channel.members == []:
    #             await channel.delete()
    #             return
            
    #         # Join to create
    #         if channel.id == 847120164611686451:
    #              category = guild.get_channel(847119816556019732)
    #              if member.name in category.voice_channels:
    #                  ch = await guild.get_channel(category.voice_channels['id'])
    #                  await member.move_to(ch)
    #                  return
    #              else:
    #             human = guild.get_role(846976407900520489)
    #             overwrites = {
    #                 guild.default_role: discord.PermissionOverwrite(view_channel=False, connect=False),
    #                 human: discord.PermissionOverwrite(view_channel=True, connect=True)
    #             }
    #             channel = await guild.create_voice_channel(member.name, overwrites=overwrites, category=category, user_limit=2)
    #             await member.move_to(channel)
    #             return

    #         else: pass


def setup(client):
    client.add_cog(Lair(client))