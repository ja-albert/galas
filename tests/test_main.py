"""Test cases for the main module."""

from datetime import datetime, tzinfo
from typing import cast

from dateutil.tz import gettz, UTC
from freezegun import freeze_time
import pytest

from galas.__main__ import (
    get_datetime_in_timezone,
    get_discord_timestamp,
    get_schedule_message,
    get_start_message,
    get_timestamp,
    parse_datetime_string,
)


GERMAN_TZ = cast(tzinfo, gettz("Europe/Berlin"))

BASE_DATE_8_UTC = datetime(2023, 8, 1, 8, 00, tzinfo=UTC)
BASE_DATE_10_UTC = datetime(2023, 8, 1, 10, 00, tzinfo=UTC)
BASE_DATE_10_GERMAN_TZ = datetime(2023, 8, 1, 10, 00, tzinfo=GERMAN_TZ)
BASE_DATE_12_GERMAN_TZ = datetime(2023, 8, 1, 12, 00, tzinfo=GERMAN_TZ)

testdata_parsing = [
    ("10:00", BASE_DATE_10_GERMAN_TZ),
    ("10:00 CEST", BASE_DATE_10_GERMAN_TZ),
    ("10:00 UTC", BASE_DATE_10_UTC),
    ("2023-09-01 10:00", datetime(2023, 9, 1, 10, 00, tzinfo=GERMAN_TZ)),
    # ("tomorrow at 10:00", datetime(2023, 8, 2, 10, 00, tzinfo=GERMAN_TZ)), TODO
]


@freeze_time("2023-08-01")
@pytest.mark.parametrize("string, expected", testdata_parsing)
def test_date_parsing(string, expected):
    assert parse_datetime_string(string) == expected


@freeze_time("2023-08-01 03:00")
@pytest.mark.parametrize("string, expected", testdata_parsing)
def test_date_parsing_on_day_change(string, expected) -> None:
    assert parse_datetime_string(string) == expected


@pytest.mark.parametrize(
    "date, new_timezone, expected",
    [
        (BASE_DATE_10_UTC, UTC, BASE_DATE_10_UTC),
        (BASE_DATE_10_UTC, GERMAN_TZ, BASE_DATE_12_GERMAN_TZ),
        (BASE_DATE_10_GERMAN_TZ, UTC, BASE_DATE_8_UTC),
        (BASE_DATE_10_GERMAN_TZ, GERMAN_TZ, BASE_DATE_10_GERMAN_TZ),
    ],
)
def test_timezone_conversion(date, new_timezone, expected) -> None:
    assert get_datetime_in_timezone(date, new_timezone) == expected


@pytest.mark.parametrize(
    "date, expected",
    [
        (BASE_DATE_8_UTC, 1690876800),
        (BASE_DATE_10_UTC, 1690884000),
        (BASE_DATE_10_GERMAN_TZ, 1690876800),
        (BASE_DATE_12_GERMAN_TZ, 1690884000),
    ],
)
def test_timestamp_conversion(date, expected) -> None:
    assert get_timestamp(date) == expected


@pytest.mark.parametrize(
    "date, flag, expected",
    [
        (BASE_DATE_8_UTC, "f", "<t:1690876800:f>"),
        (BASE_DATE_10_GERMAN_TZ, "R", "<t:1690876800:R>"),
    ],
)
def test_discord_timestamp(date, flag, expected) -> None:
    assert get_discord_timestamp(date, flag) == expected


@pytest.mark.parametrize(
    "date, level, with_timestamp, expected",
    [
        (
            BASE_DATE_8_UTC,
            1,
            True,
            "@Glitzerboys_: New Incident Level 1. Start: <t:1690876800:f> - <t:1690876800:R> - 08:00 UTC - 10:00 CEST.",
        ),
        (
            BASE_DATE_10_GERMAN_TZ,
            2,
            False,
            "@Glitzerboys_: New Incident Level 2. Start: 08:00 UTC - 10:00 CEST.",
        ),
    ],
)
def test_schedule_message(date, level, with_timestamp, expected) -> None:
    assert get_schedule_message(date, level, with_timestamp) == expected


@pytest.mark.parametrize(
    "level, expected",
    [
        (1, "@Glitzerboys_: Incident Level 1 started. 2h rule active."),
        (2, "@Glitzerboys_: Incident Level 2 started."),
    ],
)
def test_start_message(level, expected) -> None:
    assert get_start_message(level) == expected
