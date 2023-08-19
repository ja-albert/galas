from datetime import datetime, tzinfo
import os
from typing import Literal, cast

from dateutil.parser import parse
from dateutil.tz import gettz, UTC
from dateutil.utils import default_tzinfo
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

GERMAN_TZ = cast(tzinfo, gettz("Europe/Berlin"))


@client.event
async def on_ready():
    await tree.sync()
    print(f"We have logged in as {client.user}")


@tree.command()
async def schedule(interaction: discord.Interaction, level: Literal[1, 2], time: str):
    date = parse_datetime_string(time)
    discord_msg = get_schedule_message(date, level, with_timestamp=True)
    roc_msg = get_schedule_message(date, level)

    await interaction.response.send_message(roc_msg, ephemeral=True)
    await interaction.followup.send(discord_msg)


@tree.command()
async def start(interaction: discord.Interaction, level: Literal[1, 2]):
    await interaction.response.send_message(get_start_message(level))


def get_schedule_message(
    date: datetime, level: Literal[1, 2], with_timestamp: bool = False
) -> str:
    times = []
    utc_date = get_datetime_in_timezone(date, UTC)
    german_date = get_datetime_in_timezone(date, GERMAN_TZ)

    if with_timestamp:
        times.append(get_discord_timestamp(utc_date, "f"))
        times.append(get_discord_timestamp(german_date, "R"))

    times.append(get_short_timesting(utc_date))
    times.append(get_short_timesting(german_date))

    return (
        f"@Glitzerboys_: New Incident Level {level}."
        + " Start: "
        + " - ".join(times)
        + "."
    )


def parse_datetime_string(string: str, timezone: tzinfo = GERMAN_TZ) -> datetime:
    return default_tzinfo(parse(string), timezone)


def get_datetime_in_timezone(date: datetime, new_timezone: tzinfo) -> datetime:
    return date.astimezone(new_timezone)


def get_timestamp(date: datetime) -> int:
    return int(date.timestamp())


def get_discord_timestamp(date: datetime, flag: Literal["f", "R"]) -> str:
    return f"<t:{get_timestamp(date)}:{flag}>"


def get_short_timesting(date: datetime) -> str:
    return f"{date.strftime('%H:%M')} {date.tzname()}"


def get_start_message(level: Literal[1, 2]) -> str:
    message = f"@Glitzerboys_: Incident Level {level} started."
    if level == 1:
        message += " 2h rule active."
    return message


def main():
    client.run(os.getenv("DISCORD_BOT_TOKEN", ""))
