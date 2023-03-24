import discord
from discord.ext import commands
from discord.ui import View, Select
from discord import File
from easy_pil import Editor, load_image_async, load_image, Font
import requests

class MalSubmenu(Select):
    def __init__(self, data):
        self.data = data
        super().__init__(
            placeholder="Choose an option",
            options=[discord.SelectOption(label=data['data'][i]['title'], value=str(i + 1)) for i in range(len(data['data']))]
        )

    def mal_embed(self, anime):
        embed = discord.Embed(
            title = anime['title'],
            description = anime['synopsis'],
            colour = discord.Color.blue()
        )
        embed.set_footer(text="Nebrot by Holanddez")
        embed.set_image(url=anime['images']['jpg']['large_image_url'])

        keys_list = ['type', 'episodes', 'aired', 'rating', 'chapters', 'volumes', 'published', 'status', 'score', 'url']
        for key in keys_list:
            if key in anime.keys():
                if key == 'aired' or key =='published':
                    embed.add_field(name=key.capitalize(), value=anime[key]['string'], inline='false')
                else:
                    embed.add_field(name=key.capitalize(), value=anime[key], inline='false')

        return embed
    
    async def callback(self, interaction: discord.Interaction):
        self.disabled=True
        await interaction.response.edit_message(view=self.view)
        for i in range(6):
            if self.values[0] == str(i+1):
                embed = self.mal_embed(self.data['data'][i])
                await interaction.followup.send(embed=embed)
        
class MAL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def mal_api_request(self, endpoint, search=None):

        BASE_URL = "https://api.jikan.moe/v4"

        params = {
            "q": search,
            "limit": 5,
        }

        #don't know why but for some reason Jikan's API is not working with aiohttp
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params)
        response_data = response.json()

        if response.status_code != 200:
            return f"{response_data['status']} | {response_data['message']}"
        elif response_data['data'] == []:
            return "Resource not found. Please, try again."
        else:
            return response_data

    def get_favorites(self, data: dict, showType: str, bg: Editor, posX: int):
        pic_pos = -200
        for i in range(len(data['favorites'][showType][:5])):
            show = load_image(str(data['favorites'][showType][i]['images']['webp']['image_url']))
            pic_pos += 200
            show_pic = Editor(show).resize((150, 150)).circle_image()
            bg.paste(show_pic, (posX, 70 + pic_pos))
            bg.ellipse((posX, 70 + pic_pos), 150, 150, outline='white', stroke_width=3)
                
    @commands.command()
    async def malAnime(self, ctx, *, anime):
        anime_request = self.mal_api_request('anime', anime)

        select = MalSubmenu(anime_request)
        view = View()
        view.add_item(select)
        try:
            await ctx.send(view=view)
        except discord.InvalidArgument:
            await ctx.send(anime_request)

    @commands.command()
    async def malManga(self, ctx, *, manga):
        manga_request = self.mal_api_request('manga', manga)

        select = MalSubmenu(manga_request)
        view = View()
        view.add_item(select)
        try:
            await ctx.send(view=view)
        except discord.InvalidArgument:
            await ctx.send(manga_request)
    
    @commands.command()
    async def malUser(self, ctx, *, user):
        user_request = self.mal_api_request(f'users/{user}/full')
        try:
            response = user_request['data']

            bg = Editor("imgs\\bg7.jpg")

            profile_pic = await load_image_async(str(response['images']['webp']['image_url']))
            profile = Editor(profile_pic).resize((400, 400)).circle_image()

            poppins = Font.poppins(variant='regular', size=70)
            small_poppins = Font.poppins(variant='light', size=50)
            ms = Font.montserrat(variant='italic', size=65)

            bg.paste(profile, (750, 300))
            bg.ellipse((750, 300), 400, 400, outline='yellow', stroke_width=3)

            bg.text((940, 750), f"{response['username'][:25]}", color="white", font=poppins, align="center")

            #keys list
            keys_list = ['completed', 'mean_score', 'total_entries', 'episodes_watched', 'volumes_read', 'chapters_read']

            #anime statistics
            bg.text((210, 100), "Anime", color="yellow", font=ms, align="center")
            text_pos = 200
            for key in response['statistics']['anime']:
                if key in keys_list:
                    bg.text((50, text_pos), f"{key.replace('_', ' ').capitalize()}: {response['statistics']['anime'][key]}", color="white", font=small_poppins, align="left")
                    text_pos += 80

            #manga statistics
            bg.text((210, 540), "Manga", color="yellow", font=ms, align="center")
            text_pos = 640
            for key in response['statistics']['manga']:
                if key in keys_list:
                    bg.text((50, text_pos), f"{key.replace('_', ' ').capitalize()}: {response['statistics']['manga'][key]}", color="white", font=small_poppins, align="left")
                    text_pos += 80

            #favorites
            self.get_favorites(response, 'anime', bg=bg, posX=1400)
            self.get_favorites(response, 'manga', bg=bg, posX=1600)

            file = File(fp=bg.image_bytes, filename="welcome.jpg")
            await ctx.send(f"Profile URL: <{response['url']}>", file=file)
        except TypeError as e:
            print(e)
            await ctx.send(user_request)

def setup(bot):
    bot.add_cog(MAL(bot))
