import json
import pathlib

import discord
from discord.ext import commands

from bot.utils.embed import format_embed


class Submit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='submit', description="Submit your answer for the current problem.")
    async def _submit(self,
                      ctx,
                      answer: discord.Option(
                          str,
                          description="Your answer for the current problem"
                      )):
        await ctx.defer()

        # Do not allow invoking of command outside the submit channel.
        if not ctx.channel.name == 'submit':
            title = "Submit: Failure!"
            description = "You cannot use this command here! Use this command in the submit channel only."

            embed = format_embed(title, description)

            await ctx.respond(embed=embed)

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

        # Get the team (category).
        category = ctx.channel.category

        # Get the current question.
        current_question = data[category.name][-1]

        # Get the submissions channel where all submissions will go.
        submissions_channel = discord.utils.get(ctx.guild.channels, name='submissions')

        # Send the answer to the submissions channel.
        title = "Submit: Success!"
        description = f"Team: {category.name}\nQuestion: {current_question}\nAnswer: {answer}"
        embed = format_embed(title, description)

        # Create a modal for custom message.
        modal = discord.ui.Modal(title="Enter custom message to send to the team.")
        modal.add_item(discord.ui.InputText(label="Custom message"))

        async def modal_callback(interaction):
            await interaction.response.send_message("Sent custom message!")
            await ctx.send(modal.children[0].value)

        modal.callback = modal_callback

        # Create a view with correct and incorrect buttons.
        view = discord.ui.View()

        # Add correct button.
        correct = discord.ui.Button(label="Correct", style=discord.ButtonStyle.green)

        async def correct_button_callback(interaction):
            for child in view.children:
                child.disabled = True

            # await ctx.send("✅")
            await interaction.response.send_modal(modal)
            await interaction.response.edit_message(view=view)

            role = discord.utils.get(ctx.guild.roles, name=f"{category.name} {current_question}")
            await ctx.user.remove_roles(role)

        correct.callback = correct_button_callback

        # Add incorrect button.
        incorrect = discord.ui.Button(label="Incorrect", style=discord.ButtonStyle.danger)

        async def incorrect_button_callback(interaction):
            for child in view.children:
                child.disabled = True

            # await ctx.send("❌")
            await interaction.response.send_modal(modal)
            await interaction.response.edit_message(view=view)

        incorrect.callback = incorrect_button_callback

        view.add_item(correct)
        view.add_item(incorrect)

        await submissions_channel.send(embed=embed, view=view)

        # Send the "Sent!" message to the player.
        title = "Submit: Sent!"
        description = f"Your answer for {current_question} has been sent to a scorer!" \
                      " It will be evaluated and scored shortly."
        embed = format_embed(title, description)
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Submit(bot))
