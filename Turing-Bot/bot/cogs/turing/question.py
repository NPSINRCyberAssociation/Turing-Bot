import logging
import os
import random

import discord
from discord.ext import commands

from bot.utils.embed import format_embed

logger = logging.getLogger(__name__)


class Question(commands.Cog):
    def __int__(self, bot):
        self.bot = bot

    @commands.slash_command(name='question', description="Provide a question to solve. Has a timeout for 15 minutes.")
    async def _question(self,
                        ctx,
                        difficulty: discord.Option(
                            str,
                            description="The difficulty of the question.",
                            choices=[
                                "easy",
                                "hard"
                            ]
                        )):
        await ctx.defer()

        # Send a random question from the data directory.
        questions_list = {
            "easy": [os.path.join(os.path.relpath(path), name) for path, sub_dirs, files in os.walk('bot/data/questions/easy') for name in files],
            "hard": [os.path.join(os.path.relpath(path), name) for path, sub_dirs, files in os.walk('bot/data/questions/hard') for name in files],
        }

        path = random.choice(questions_list[difficulty])

        file = discord.File(path)

        title = "Question: Success!"
        description = f"Provided a/an {difficulty} question!"

        embed = format_embed(title, description)

        await ctx.respond(embed=embed, file=file)

        logger.info(
            f"{ctx.guild.name} -> Provided a/an {difficulty} question!"
        )
    #
    # @_question.error
    # async def on_application_command_error(self, ctx, error):
    #     if isinstance(error, commands.MissingPermissions):
    #         title = "Purge: Error!"
    #         description = f"Unable to purge: The user has insufficient permissions to purge!"
    #
    #         embed = format_embed(title, description)
    #         await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Question(bot))
