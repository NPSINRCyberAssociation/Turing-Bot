import asyncio
import json
import logging
import os
import pathlib
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

        # Do not allow invoking of command outside the problems channel.
        if not ctx.channel.name == 'problems':
            title = "Question: Failure!"
            description = "You cannot use this command here! Use this command in the problems channel only."

            embed = format_embed(title, description)

            await ctx.respond(embed=embed)

            return

        # Read the question status data file, or create it if it doesn't exist.
        if not pathlib.Path('bot/data/questions/data.json').is_file():
            data = {}

            for category in ctx.guild.categories:
                data[category.name] = []

            with open('bot/data/questions/data.json', 'w+') as data_file:
                json.dump(data, data_file)
                data_file.close()

        else:
            with open('bot/data/questions/data.json', 'r') as data_file:
                data = json.load(data_file)
                data_file.close()

        # Get the team (category)
        category = ctx.channel.category

        # Get a random question from the data directory.
        questions_list = {
            "easy": [os.path.join(os.path.relpath(path), name) for path, sub_dirs, files in
                     os.walk('bot/data/questions/easy') for name in files],
            "hard": [os.path.join(os.path.relpath(path), name) for path, sub_dirs, files in
                     os.walk('bot/data/questions/hard') for name in files],
        }

        path = random.choice(
            [question for question in questions_list[difficulty] if question not in data[category.name]])
        name = '-'.join(path.split('\\')[-1].split('.')[0].split(' ')).lower()

        # Add the current question to data file.
        data[category.name].append(name)

        with open('bot/data/questions/data.json', 'w') as data_file:
            json.dump(data, data_file)
            data_file.close()

        # Create a channel in that category with the same name as the question.
        # await ctx.guild.create_text_channel(f"{name}", category=category)
        # channel = discord.utils.get(ctx.guild.channels, name=name)

        # Create and add question muted role to the user.
        await ctx.guild.create_role(name=f"{category.name} {name}")

        role = discord.utils.get(ctx.guild.roles, name=f"{category.name} {name}")

        await ctx.channel.set_permissions(role, read_messages=True, send_messages=False)
        await ctx.user.add_roles(role)

        title = "Question: Success!"
        description = "Created a question! Your question timeout of 15 minutes has begin. You can ask for another " \
                      "question only if you solve the current question or the timeout of 15 minutes runs out. "
        file = discord.File(path)
        embed = format_embed(title, description)

        await ctx.respond(embed=embed, file=file)

        # Send the info message to the user.
        # title = "Question: Success!"
        # description = f"Created a question. Check {channel.mention} to access the " \
        #               f"question!\n" \
        #               "Your question timeout of 15 minutes has begin. You can get another question only if you solve " \
        #               "the current one, or the time of 15 minutes runs out."
        #
        # embed = format_embed(title, description)
        #
        # await ctx.respond(embed=embed)

        # Send the question to the new channel.
        # file = discord.File(path)
        # await channel.send(file=file)

        logger.info(
            f"{ctx.guild.name} -> Provided a/an {difficulty} question!"
        )

        # Sleep for 15 minutes, and then send the timeout removal message if the timeout is still present.
        await asyncio.sleep(900)

        try:
            title = "Question: Success!"
            description = "Your timeout of 15 minutes has passed! You can request for a new question now."

            embed = format_embed(title, description)

            await ctx.send(embed=embed)
            await ctx.user.remove_roles(role)

        except commands.RoleNotFound:
            pass


def setup(bot):
    bot.add_cog(Question(bot))
