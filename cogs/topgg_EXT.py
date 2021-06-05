import discord, dbl, asyncio, logging
from discord.ext import commands, tasks


class TopGG(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijc5NTA5OTY5MDYwOTI3OTAwNiIsImJvdCI6dHJ1ZSwiaWF0IjoxNjIyODUyNjg5fQ.-zEp0VTyX2hvyH6ktUbFFUQ_TXEfE4LZvp654x94xoE'
        self.dblpy = dbl.DBLClient(self.client, self.token)


    @tasks.loop(minutes=30.0)
    async def update_stats(self):
        logger.info('Attempting to post server count')
        try:
            await self.dblpy.post_guild_count()
            logger.info('Posted server count ({})'.format(self.dblpy.guild_count()))
        except Exception as e:
            logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))


        await asyncio.sleep(1800)

def setup(client):
    global logger
    logger = logging.getLogger('client')
    client.add_cog(TopGG(client))