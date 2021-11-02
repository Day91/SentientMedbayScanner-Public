import discord
from discord.ext import commands
class Admin(commands.Cog):
    def __init__(self,client):
        self.client = client
    @commands.command(brief='Reload a cog.')
    @commands.is_owner()
    async def reload(self,ctx,cog):
        self.client.unload_extension(f'cogs.{cog}')
        self.client.load_extension(f'cogs.{cog}')
        await ctx.send("Cog reloaded!")
def setup(client):
    client.add_cog(Admin(client))