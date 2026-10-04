import asyncio
import logging
import os

import discord
from discord import app_commands
from discord.ext import commands, tasks

from config import GITHUB_STATE_FILE
from services.github import (
    parse_repository_url,
    get_repository,
    get_latest_release,
)
from services.permissions import (
    allowed_channel,
    owner_only,
)
from services.utils import (
    load_json,
    save_json,
)

logger = logging.getLogger(__name__)


class GitHub(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.github_loop.start()

    def cog_unload(self):
        self.github_loop.cancel()

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def load_repositories(self):
        state = load_json(GITHUB_STATE_FILE)

        if "repositories" not in state:
            state["repositories"] = {}

        return state

    def save_repositories(self, state):
        save_json(
            GITHUB_STATE_FILE,
            state
        )

    # --------------------------------------------------
    # GitHub update checker
    # --------------------------------------------------

    @tasks.loop(hours=6)
    async def github_loop(self):

        try:
            await self.check_repositories()

        except Exception:
            logger.exception(
                "Error while checking GitHub repositories."
            )

    @github_loop.before_loop
    async def before_github_loop(self):

        await self.bot.wait_until_ready()

        logger.info(
            "GitHub update checker is ready."
        )

        # Check immediately after startup
        await self.check_repositories()

    async def check_repositories(self):

        channel_id = os.getenv(
            "GITHUB_UPDATES_CHANNEL_ID"
        )

        if not channel_id:
            logger.error(
                "GITHUB_UPDATES_CHANNEL_ID "
                "is not configured."
            )
            return

        channel = self.bot.get_channel(
            int(channel_id)
        )

        if channel is None:
            try:
                channel = await self.bot.fetch_channel(
                    int(channel_id)
                )
            except discord.HTTPException:
                logger.exception(
                    "Failed to fetch GitHub updates channel."
                )
                return

        state = self.load_repositories()

        repositories = state["repositories"]

        for repository_url, repository_data in repositories.items():

            owner = repository_data["owner"]
            repo = repository_data["repo"]
            last_release = repository_data.get(
                "last_release"
            )

            release = await asyncio.to_thread(
                get_latest_release,
                owner,
                repo
            )

            if release is None:
                logger.info(
                    "No release found for %s/%s",
                    owner,
                    repo
                )
                continue

            release_id = str(
                release["id"]
            )

            # First check:
            # save current release without notifying.
            if last_release is None:

                repository_data["last_release"] = (
                    release_id
                )

                continue

            # Nothing changed
            if last_release == release_id:
                continue

            # New release
            repository_data["last_release"] = (
                release_id
            )

            await self.send_release_notification(
                channel,
                release
            )

            logger.info(
                "New GitHub release detected: %s/%s - %s",
                owner,
                repo,
                release.get("tag_name", "Unknown")
            )

        self.save_repositories(state)

    async def send_release_notification(
        self,
        channel,
        release
    ):

        name = release.get(
            "name"
        ) or release.get(
            "tag_name",
            "New release"
        )

        tag = release.get(
            "tag_name",
            "Unknown"
        )

        repository = release.get(
            "html_url",
            ""
        )

        author = release.get(
            "author",
            {}
        )

        author_name = author.get(
            "login",
            "Unknown"
        )

        embed = discord.Embed(
            title=f"🚀 {name}",
            description=(
                f"A new GitHub release is available!\n\n"
                f"**Version:** `{tag}`\n"
                f"**Author:** `{author_name}`"
            ),
            url=repository,
            color=discord.Color.blurple()
        )

        published_at = release.get(
            "published_at"
        )

        if published_at:
            embed.add_field(
                name="Published",
                value=published_at,
                inline=False
            )

        embed.set_footer(
            text="GitHub Release Monitor"
        )

        await channel.send(
            embed=embed
        )


    github_group = app_commands.Group(
        name="github",
        description="Manage GitHub repositories."
    )

    # --------------------------------------------------
    # /github add
    # --------------------------------------------------

    @github_group.command(
        name="add",
        description="Add a GitHub repository to monitor."
    )
    @app_commands.describe(link="GitHub repository URL.")
    @allowed_channel("GITHUB_COMMANDS_CHANNEL_ID")
    @owner_only()
    async def github_add(
        self,
        interaction: discord.Interaction,
        link: str
    ):
        # Acknowledge the interaction immediately.
        await interaction.response.defer()

        parsed = parse_repository_url(link)

        if parsed is None:
            await interaction.followup.send(
                "❌ Invalid GitHub repository URL.",
                ephemeral=True
            )
            return

        owner, repo = parsed

        repository = await asyncio.to_thread(
            get_repository,
            owner,
            repo
        )

        if repository is None:
            await interaction.followup.send(
                "❌ GitHub repository not found.",
                ephemeral=True
            )
            return

        state = self.load_repositories()
        repositories = state["repositories"]

        normalized_url = f"https://github.com/{owner}/{repo}"

        if normalized_url in repositories:
            await interaction.followup.send(
                "⚠️ This repository is already being monitored.",
                ephemeral=True
            )
            return

        latest_release = await asyncio.to_thread(
            get_latest_release,
            owner,
            repo
        )

        repositories[normalized_url] = {
            "owner": owner,
            "repo": repo,
            "last_release": (
                str(latest_release["id"])
                if latest_release
                else None
            ),
            "version": (
                latest_release.get("tag_name", "Unknown")
                if latest_release
                else "No releases"
            )
        }

        self.save_repositories(state)

        # Public success message.
        await interaction.followup.send(
            f"✅ Now monitoring **{owner}/{repo}** for new releases."
        )

    # --------------------------------------------------
    # /github remove
    # --------------------------------------------------

    @github_group.command(
        name="remove",
        description="Stop monitoring a GitHub repository."
    )
    @app_commands.describe(
        link="GitHub repository URL."
    )
    @allowed_channel(
        "GITHUB_COMMANDS_CHANNEL_ID"
    )
    @owner_only()
    async def github_remove(
        self,
        interaction: discord.Interaction,
        link: str
    ):

        parsed = parse_repository_url(link)

        if parsed is None:
            await interaction.response.send_message(
                "❌ Invalid GitHub repository URL.",
                ephemeral=True
            )
            return

        owner, repo = parsed

        normalized_url = (
            f"https://github.com/{owner}/{repo}"
        )

        state = self.load_repositories()

        repositories = state["repositories"]

        if normalized_url not in repositories:

            await interaction.response.send_message(
                "❌ This repository is not being monitored.",
                ephemeral=True
            )
            return

        del repositories[normalized_url]

        self.save_repositories(state)

        await interaction.response.send_message(
            f"🗑️ Stopped monitoring **{owner}/{repo}**."
        )

    # --------------------------------------------------
    # /github list
    # --------------------------------------------------

    @github_group.command(
        name="list",
        description="Show monitored GitHub repositories."
    )
    @allowed_channel("GITHUB_COMMANDS_CHANNEL_ID")
    async def github_list(
        self,
        interaction: discord.Interaction
    ):
        state = self.load_repositories()
        repositories = state["repositories"]

        if not repositories:
            await interaction.response.send_message(
                "📦 No GitHub repositories are being monitored."
            )
            return

        embed = discord.Embed(
            title="🐙 Monitored GitHub Repositories",
            description="Repositories currently monitored for new releases.",
            color=discord.Color.blurple()
        )

        for url, data in repositories.items():

            version = data.get(
                "version",
                "Unknown"
            )

            # Remove "v" from versions like v2.0
            if version.lower().startswith("v"):
                version = version[1:]

            embed.add_field(
                name=f"📦 {data['owner']}/{data['repo']}",
                value=(
                    f"**Version:** `{version}`\n"
                    f"🔗 [Repository]({url})"
                ),
                inline=False
            )

        embed.set_footer(
            text=f"{len(repositories)} repositories monitored"
        )

        await interaction.response.send_message(
            embed=embed
        )

async def setup(bot):
    await bot.add_cog(GitHub(bot))