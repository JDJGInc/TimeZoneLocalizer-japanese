import traceback

import discord
from icu import Locale, TimeZone


def list_timezones(locale: discord.Locale, timezones: list[str]):

    match locale:
        case discord.Locale.american_english:
            cleaned_locale = locale.value.replace("-", "_")

        case discord.Locale.british_english:
            cleaned_locale = locale.value.replace("-", "_")

        case default:
            cleaned_locale = discord.Locale.japanese.value

    timezones_dictionary = {}
    for timezone in timezones:
        try:
            tz = TimeZone.createTimeZone(timezone)
            locale = Locale(cleaned_locale)
            timezones_dictionary[timezone] = timezone
            timezone_localized = tz.getDisplayName(True, TimeZone.LONG, locale)
            if timezone_localized.lower().startswith("unknown region"):
                timezone_localized = timezone

            timezones_dictionary[timezone_localized] = timezone

        except Exception as e:
            traceback.print_exception(e)

    return timezones_dictionary
