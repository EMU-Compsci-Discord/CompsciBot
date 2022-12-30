"""
This cog adds a command for accessing ratemyprofessor
"""


import ratemyprofessor
import nextcord
from nextcord.ext import commands
from nextcord import SlashOption

from constants import SUCCESS_COLOR


class RateMyProfessor(commands.Cog, name="rate my professor"):
    """
    This cog adds a command for accessing ratemyprofessor
    """

    def __init__(self, bot):
        self.bot = bot
        self.profImages = {
            "William Sverdlik": "https://www.emich.edu/computer-science/images/faculty/w-sverdlik.jpg",
            "Zenia Bahorski": "https://www.emich.edu/computer-science/images/faculty/zbahorski.jpg",
            "Andrii Kashliev": "https://www.emich.edu/computer-science/images/faculty/andreii-kashliev.jpg",
            "Krish Narayanan": "https://www.emich.edu/computer-science/images/faculty/k-narayanan.jpg",
            "Siyuan Jiang": "https://www.emich.edu/computer-science/images/faculty/s-jiang.jpg",
        }

    @nextcord.slash_command(name="rmp", description="Check out what RateMyProfessor has to say about a professor!")
    async def rmp(self, interaction: nextcord.Interaction, professorname: str = SlashOption(name="professorname", description="The name of the professor you want to look up", required=True)):
        """
        [(Required) Professor name] Check out what RateMyProfessor has to say about a professor!
        """
        try:
            EMU = ratemyprofessor.get_school_by_name("Eastern Michigan University")
            prof = ratemyprofessor.get_professor_by_school_and_name(EMU, professorname)

            ratingsBest = sorted([rating for rating in prof.get_ratings() if rating.comment],
                                 key=lambda rating: (rating.rating, rating.date))
            bestRating = ratingsBest[-1]

            ratingsWorst = sorted([rating for rating in prof.get_ratings() if rating.comment],
                                  key=lambda rating: (-rating.rating, rating.date))
            worstRating = ratingsWorst[-1]

            profEmbed = self.buildProfEmbed(prof)
            bestembed = self.buildRatingEmbed(nextcord.Embed(title=f"Best Rating for {prof.name}", color=SUCCESS_COLOR),
                                              bestRating)
            worstembed = self.buildRatingEmbed(nextcord.Embed(title=f"Worst Rating for {prof.name}", color=SUCCESS_COLOR),
                                               worstRating)

            await interaction.response.send_message(embed=profEmbed)
            await interaction.followup.send(embed=bestembed)
            await interaction.followup.send(embed=worstembed)
        except:
            await interaction.response.send_message(f"Could not find professor '{professorname}'. Try only using a last name or check your spelling!")

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
        embed = nextcord.Embed(
            title=prof,
            color=SUCCESS_COLOR
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
