import asyncio
import traceback
import typing
import zoneinfo

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from icu import Locale, TimeZone

from utils import fuzzy
from utils.extra import list_timezones


class ConversionUtil(commands.Cog):
    "便利なものを変換するための歯車。"

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.available_timezones = sorted(list(await asyncio.to_thread(zoneinfo.available_timezones)))

    @app_commands.user_install()
    @app_commands.guild_install()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(
        timezone="変換したいタイムゾーンを選択します。",
    )
    @app_commands.command(description="メッセージのタイムスタンプを地域の時間に変換するコマンド。", name="コンバート_タイムゾーン")
    async def convert_timezone(self, interaction: discord.Interaction, timezone: typing.Optional[str] = None):

        timezones = self.available_timezones

        if not timezone:
            timestamp = discord.utils.format_dt(interaction.created_at)
            embed = discord.Embed(title="時刻:", description=timestamp)
            embed.set_footer(text="タイムゾーン: 指定なし")

        elif not timezone in timezones:
            timestamp = discord.utils.format_dt(interaction.created_at)
            embed = discord.Embed(title="時刻:", description=timestamp)
            embed.set_footer(text="タイムゾーン: 見つかりません")

        else:
            now_tz = interaction.created_at.astimezone(zoneinfo.ZoneInfo(timezone))
            am_pm_format = now_tz.strftime("%I:%M:%S %p")
            twenty_four_format = now_tz.strftime("%H:%M:%S")
            first_format = now_tz.strftime("%Y-%m-%d")
            second_format = now_tz.strftime("%Y-%d-%m")
            third_format = now_tz.strftime("%d-%m-%Y")
            fourth_format = now_tz.strftime("%m-%d-%Y")

            # possibly do colors depending on time but not sure.
            # shrug
            try:
                locale = interaction.locale
                tz = TimeZone.createTimeZone(timezone)
                match locale:
                    case discord.Locale.american_english:
                        cleaned_locale = locale.value.replace("-", "_")

                    case discord.Locale.british_english:
                        cleaned_locale = locale.value.replace("-", "_")

                    case default:
                        cleaned_locale = discord.Locale.japanese.value

                locale = Locale(cleaned_locale)
                localized_timezone = tz.getDisplayName(True, TimeZone.LONG, locale)

                if localized_timezone.lower().startswith("unknown region"):
                    localized_timezone = timezone

            except Exception as e:
                localized_timezone = timezone
                traceback.print_exc(e)

            embed = discord.Embed(
                title="時刻:",
                description=f"12時間表記: {am_pm_format}\n24時間表記: {twenty_four_format}\n\nYYYY-MM-DD: {first_format} \nYYYY-DD-MM: {second_format}\nDD-MM-YYYY: {third_format}\nMM-DD-YYYY: {fourth_format}",
            )
            embed.set_footer(text=f"タイムゾーン: {timezone}\nローカライズされたタイムゾーン: {localized_timezone}")

        await interaction.response.send_message(embed=embed)

    @convert_timezone.autocomplete("timezone")
    async def convert_timezone_autocomplete(self, interaction: discord.Interaction, current: str) -> list[Choice]:

        timezones = self.available_timezones
        localized_timezones = await asyncio.to_thread(list_timezones, interaction.locale, timezones)

        all_choices = [Choice(name=timezone, value=localized_timezones[timezone]) for timezone in localized_timezones]

        if not (current):
            return all_choices[0:25]

        filtered_results = fuzzy.finder(current, localized_timezones.keys())
        results = [Choice(name=result, value=localized_timezones[result]) for result in filtered_results]

        return results[0:25]

    @convert_timezone.error
    async def convert_timezone_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f"{error}! 開発者に問い合わせてください。", ephemeral=True)
        print(interaction.command)
        traceback.print_exc()

async def setup(bot):
    await bot.add_cog(ConversionUtil(bot))
