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
        embed.add_field(name='Type', value=anime['type'], inline='false')
        try:
            embed.add_field(name='Episodes', value=anime['episodes'], inline='false')
            embed.add_field(name='Aired', value=anime['aired']['string'], inline='false')
            embed.add_field(name='Rating', value=anime['rating'], inline='false')
        except KeyError:
            embed.add_field(name='Chapters', value=anime['chapters'], inline='false')
            embed.add_field(name='Volumes', value=anime['volumes'], inline='false')
            embed.add_field(name='Published', value=anime['published']['string'], inline='false')
        embed.add_field(name='Status', value=anime['status'], inline='false')
        embed.add_field(name='Score', value=anime['score'], inline='false')
        embed.add_field(name='MyAnimeList', value=anime['url'], inline='false')

        return embed
    
    async def callback(self, interaction: discord.Interaction):
        self.disabled=True
        await interaction.response.edit_message(view=self.view)
        if self.values[0] == "1":
            embed = self.mal_embed(self.data['data'][0])
            await interaction.followup.send(embed=embed)
        if self.values[0] == "2":
            embed = self.mal_embed(self.data['data'][1])
            await interaction.followup.send(embed=embed)
        if self.values[0] == "3":
            embed = self.mal_embed(self.data['data'][2])
            await interaction.followup.send(embed=embed)
        if self.values[0] == "4":
            embed = self.mal_embed(self.data['data'][3])
            await interaction.followup.send(embed=embed)
        if self.values[0] == "5":
            embed = self.mal_embed(self.data['data'][4])
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

    def get_favourites(self, data: dict, showType: str):
        favs = []
        for i in range(len(data['favorites'][showType][:5])):
            show = load_image(str(data['favorites'][showType][i]['images']['webp']['image_url']))
            favs.append(show)
        return favs

    def generate_favs_image(self, bg: Editor, posX: int, showsList: list):
        pic_pos = -200
        for show in showsList:
            pic_pos += 200
            anime_pic = Editor(show).resize((150, 150)).circle_image()
            bg.paste(anime_pic, (posX, 70 + pic_pos))
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

            #anime statistics
            bg.text((210, 100), "Anime", color="yellow", font=ms, align="center")
            bg.text((50, 200), f"Completed: {response['statistics']['anime']['completed']}", color="white", font=small_poppins, align="left")
            bg.text((50, 280), f"Mean Score: {response['statistics']['anime']['mean_score']}", color="white", font=small_poppins, align="left")
            bg.text((50, 360), f"Total Entries: {response['statistics']['anime']['total_entries']}", color="white", font=small_poppins, align="left")
            bg.text((50, 440), f"Eps Watched: {response['statistics']['anime']['episodes_watched']}", color="white", font=small_poppins, align="left")

            #manga statistics
            bg.text((210, 540), "Manga", color="yellow", font=ms, align="center")
            bg.text((50, 640), f"Completed: {response['statistics']['manga']['completed']}", color="white", font=small_poppins, align="left")
            bg.text((50, 720), f"Mean Score: {response['statistics']['manga']['mean_score']}", color="white", font=small_poppins, align="left")
            bg.text((50, 800), f"Total Entries: {response['statistics']['manga']['total_entries']}", color="white", font=small_poppins, align="left")
            bg.text((50, 880), f"Volumes Read: {response['statistics']['manga']['volumes_read']}", color="white", font=small_poppins, align="left")
            bg.text((50, 960), f"Chapters Read: {response['statistics']['manga']['chapters_read']}", color="white", font=small_poppins, align="left")

            #favorites
            fav_animes = self.get_favourites(response, 'anime')
            self.generate_favs_image(bg=bg, posX=1400, showsList=fav_animes)

            fav_mangas = self.get_favourites(response, 'manga')
            self.generate_favs_image(bg=bg, posX=1600, showsList=fav_mangas)

            file = File(fp=bg.image_bytes, filename="welcome.jpg")
            await ctx.send(f"Profile URL: <{response['url']}>", file=file)
        except TypeError as e:
            print(e)
            await ctx.send(user_request)

def setup(bot):
    bot.add_cog(MAL(bot))
