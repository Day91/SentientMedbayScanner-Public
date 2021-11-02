import discord
import json
from discord.ext import commands
from discord.utils import get
intents = discord.Intents.all()
class Main(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.jsonfile = open("curgame.json","r+")
        self.jsondata = json.loads(self.jsonfile.read())
    def updatejson(self):
        self.jsonfile.seek(0)
        self.jsondata = json.loads(self.jsonfile.read())
    def changejson(self):
        self.jsonfile.close()
        self.jsonfile = open("curgame.json","w")
        self.jsonfile.write(json.dumps(self.jsondata))
        self.jsonfile.close()
        self.jsonfile = open("curgame.json","r+")
    @commands.command(brief='Ping')
    async def ping(self,ctx):
        await ctx.send(f"Pong!\n{round(self.client.latency * 1000)}ms")
    @commands.command(brief="Update game code")
    @commands.has_any_role("Doctor","Admin","Mod")
    async def updatecode(self,ctx):
        self.updatejson()
        channel = self.client.get_channel(779790967624433694)
        await channel.edit(name=f"Game Code: {self.jsondata['metadata']['game-code']}")
        await ctx.send("Game code updated!")
    @commands.command(brief="Change game code")
    @commands.has_any_role("Doctor","Admin","Mod")
    async def changecode(self,ctx,code):
        self.jsondata['metadata']['game-code'] = code
        self.changejson()
        self.updatejson()
        await ctx.send('Changed game code!')
    @commands.command(brief="Show code")
    async def showcode(self,ctx):
        code = self.jsondata['metadata']['game-code']
        await ctx.send(code)
    @commands.command(brief="Start game")
    @commands.has_any_role("Doctor","Admin","Mod")
    async def start(self,ctx):
        channel = self.client.get_channel(695629673228402718)
        members = list(channel.voice_states.keys())
        self.jsondata['game']['players'] = members
        self.jsondata['game']['dead'] = []
        self.jsondata['metadata']['game-status'] = 'on'
        self.changejson()
        self.updatejson()
        await ctx.send(f'Game started with {len(members)} players')
    @commands.command(brief="Mark a player as dead")
    @commands.has_any_role("Doctor","Admin","Mod")
    async def dead(self,ctx,user: discord.Member):
        if user.id not in self.jsondata['game']['dead']:
            self.jsondata['game']['dead'].append(user.id)
            self.changejson()
            self.updatejson()
            await ctx.send(f"User {user.display_name} marked as dead")
        else:
            await ctx.send("User already dead!")
        if self.jsondata['game']['meeting']:
            await user.edit(mute=True,deafen=False)
        else:
            await user.edit(mute=False,deafen=False)
    @commands.command(brief="Unmark a player as dead")
    @commands.has_any_role("Doctor","Admin","Mod")
    async def revive(self,ctx,user: discord.Member):
        if user.id in self.jsondata['game']['dead']:
            self.jsondata['game']['dead'].remove(user.id)
            self.changejson()
            self.updatejson()
            await ctx.send("User marked as alive")
        else:
            await ctx.send("User not dead!")
        if self.jsondata['game']['meeting']:
            await user.edit(mute=False,deafen=False)
        else:
            await user.edit(mute=True,deafen=True)
    @commands.command(brief="Go into the round, muting + deafening everyone except the dead.")
    @commands.has_any_role("Doctor","Admin","Mod")
    async def round(self,ctx):
        for player in self.jsondata['game']['players']:
            obj = ctx.guild.get_member(player)
            try:
                await obj.edit(mute=True,deafen=True)
            except:
                await ctx.send(f"{obj.mention} is not in the VC. This may cause issues. Tell this player to join waiting room so they can be changed accordingly.")
        for player in self.jsondata['game']['dead']:
            obj = ctx.guild.get_member(player)
            try:
                await obj.edit(mute=False,deafen=False)
            except:
                await ctx.send(f"{obj.mention} is not in the VC. This may cause issues. Tell this player to join waiting room so they can be changed accordingly.")
        self.jsondata['game']['meeting'] = False
        self.changejson()
        self.updatejson()
        await ctx.send("Deafened the alive, unmuted the dead")
    @commands.command(brief="Go out of the round, keep the dead muted and let everyone else out!")
    @commands.has_any_role("Doctor","Admin","Mod")
    async def meeting(self,ctx):
        for player in self.jsondata['game']['dead']:
            obj = get(self.client.get_all_members(), id=player)
            try:
                await obj.edit(mute=True,deafen=False)
            except:
                await ctx.send(f"{obj.mention} is not in the VC. This may cause issues. Tell this player to join waiting room so they can be changed accordingly.")
        for player in self.jsondata['game']['players']:
            if player not in self.jsondata['game']['dead']:
                obj = get(self.client.get_all_members(), id=player)
                try:
                    await obj.edit(mute=False,deafen=False)
                except:
                    await ctx.send(f"{obj.mention} is not in the VC. This may cause issues. Tell this player to join waiting room so they can be changed accordingly.")
        self.jsondata['game']['meeting'] = True
        self.changejson()
        self.updatejson()
        await ctx.send("Meeting settings activated!")
    @commands.command(brief="End round")
    @commands.has_any_role("Doctor","Admin","Mod")
    async def end(self,ctx):
        for player in self.jsondata['game']['players']:
            try:
                obj = get(self.client.get_all_members(), id=player)
                await obj.edit(mute=False,deafen=False)
            except:
                pass
        self.jsondata['game']['players'] = []
        self.jsondata['game']['dead'] = []
        self.jsondata['game']['meeting'] = False
        self.jsondata['metadata']['game-status'] = 'off'
        self.changejson()
        self.updatejson()
        await ctx.send("Game ended.")
def setup(client):
    client.add_cog(Main(client))
