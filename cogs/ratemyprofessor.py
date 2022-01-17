import os
import sys
import discord
import yaml
from discord.ext import commands
import ratemyprofessor

if "CompsciBot" not in str(os.getcwd()):
    os.chdir("./CompsciBot")
with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

class RateMyProfessor(commands.Cog, name="rate my professor"):
    def __init__(self, bot):
        self.bot = bot
        self.profImages = {
            "William Sverdlik": "https://www.emich.edu/computer-science/images/faculty/w-sverdlik.jpg",
            "Zenia Bahorski": "https://www.emich.edu/computer-science/images/faculty/zbahorski.jpg",
            "Andrii Kashliev": "https://www.emich.edu/computer-science/images/faculty/andreii-kashliev.jpg",
            "Krish Narayanan": "https://www.emich.edu/computer-science/images/faculty/k-narayanan.jpg",
            "Siyuan Jiang": "https://www.emich.edu/computer-science/images/faculty/s-jiang.jpg",
        }

    @commands.command(name="rmp")
    async def rmp(self, context, *professorArgs):
        """
        [(Required) Professor name] Check out what RateMyProfessor has to say about a professor!
        """
        professorSearchTerm = " ".join(professorArgs)
        EMU = ratemyprofessor.get_school_by_name("Eastern Michigan University")
        prof = ratemyprofessor.get_professor_by_school_and_name(EMU, professorSearchTerm)

        ratingsBest = sorted([rating for rating in prof.get_ratings() if rating.comment], key=lambda rating: (rating.rating, rating.date))
        bestRating = ratingsBest[-1]

        ratingsWorst = sorted([rating for rating in prof.get_ratings() if rating.comment], key=lambda rating: (-rating.rating, rating.date))
        worstRating = ratingsWorst[-1]

        profEmbed = self.buildProfEmbed(prof)
        bestembed = self.buildRatingEmbed(discord.Embed(title=f"Best Rating for {prof.name}", color=config["success"]), bestRating)
        worstembed = self.buildRatingEmbed(discord.Embed(title=f"Worst Rating for {prof.name}",color=config["success"]), worstRating)
        
        await context.send(embed=profEmbed)
        await context.send(embed=bestembed)
        await context.send(embed=worstembed)

    def buildRatingEmbed(self, embed, rating):
        if rating.rating:
            embed.add_field(
                name="Rating",
                value=rating.rating,
                inline=True
            )

        if rating.difficulty:
            embed.add_field(
                name="Difficulty",
                value=rating.difficulty,
                inline=True
            )

        if rating.date:
            embed.add_field(
                name="Date",
                value=rating.date,
                inline=True
            )

        if rating.take_again:
            embed.add_field(
                name="Would Take Again",
                value=rating.take_again,
                inline=True
            )

        if rating.grade:
            embed.add_field(
                name="Grade Recieved",
                value=rating.grade,
                inline=True
            )

        if rating.comment:
            embed.add_field(
                name="Comment",
                value=rating.comment,
                inline=False
            )

        return embed
    
    def buildProfEmbed(self, prof):
        embed = discord.Embed(
            title=prof,
            color=config["success"]
        )

        if prof.name in self.profImages:
            embed.set_image(url=self.profImages[prof.name])
        
        embed.add_field(
            name="Department",
            value=prof.department,
            inline=False
        )

        embed.add_field(
            name="Average Rating",
            value=prof.rating,
            inline=False
        )

        embed.add_field(
            name="Difficulty",
            value=prof.difficulty,
            inline=True
        )

        embed.add_field(
            name="Would Take Again",
            value=f"{prof.would_take_again}%",
            inline=False
        )

        embed.add_field(
            name="Number of Ratings",
            value=prof.num_ratings,
            inline=False
        )

        embed.add_field(
            name="Link to RateMyProfessor page",
            value=f"https://www.ratemyprofessors.com/ShowRatings.jsp?tid={prof.id}",
            inline=False
        )

        return embed

def setup(bot):
    bot.add_cog(RateMyProfessor(bot))
