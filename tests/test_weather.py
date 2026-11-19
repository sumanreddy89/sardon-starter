"""Tests for the clothing and warning rules in tools/weather.py (no network)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import json  # noqa: E402
import urllib.error  # noqa: E402
from unittest import mock  # noqa: E402

import weather  # noqa: E402
from weather import known_place, outfit_for, outlook_day, summarise_day  # noqa: E402


def hours(temp, feels=None, rain=0.0, prob=0, gust=3, symbol="cloudy", uv=0, start=7, end=23, day="2026-11-17"):
    return [{"local": f"{day}T{h:02d}:00:00+02:00", "temp": temp, "feels": temp if feels is None else feels,
             "temp_lo": temp - 0.5, "temp_hi": temp + 0.5, "gust": gust, "wind": gust / 2, "uv": uv,
             "rain": rain, "rain_prob": prob, "symbol": symbol} for h in range(start, end)]


class Outfit(unittest.TestCase):
    def test_bands_follow_feels_like(self):
        self.assertIn("Heavy down coat", outfit_for(-20, 0, 0, 3, False, False, 0))
        self.assertIn("Winter coat", outfit_for(-8, 0, 0, 3, False, False, 0))
        self.assertIn("Warm coat", outfit_for(0, 0, 0, 3, False, False, 0))
        self.assertIn("Medium jacket", outfit_for(5, 0, 0, 3, False, False, 0))
        self.assertIn("Light jacket", outfit_for(12, 0, 0, 3, False, False, 0))
        self.assertEqual(outfit_for(25, 0, 0, 3, False, False, 0), ["T-shirt"])

    def test_rain_adds_umbrella_or_hood_when_windy(self):
        self.assertIn("Umbrella or waterproof", outfit_for(10, 2, 80, 5, False, False, 0))
        self.assertIn("Waterproof shell with a hood", outfit_for(10, 2, 80, 15, False, False, 0))
        self.assertNotIn("Umbrella or waterproof", outfit_for(10, 0, 10, 5, False, False, 0))

    def test_snow_ice_and_sun(self):
        self.assertIn("Shoes with good grip", outfit_for(-1, 0, 0, 3, False, True, 0))
        self.assertIn("Waterproof boots", outfit_for(1, 2, 80, 3, True, False, 0))
        self.assertNotIn("Umbrella or waterproof", outfit_for(1, 2, 80, 3, True, False, 0))
        self.assertIn("Sunglasses and sunscreen", outfit_for(22, 0, 0, 3, False, False, 6))


class Day(unittest.TestCase):
    def test_dry_mild_day(self):
        d = summarise_day(hours(9))
        self.assertEqual(d["flags"], [])
        self.assertIn("dry", d["summary"])
        self.assertEqual(d["feels_min"], 9)

    def test_feels_like_drives_the_outfit(self):
        d = summarise_day(hours(4, feels=-2))
        self.assertIn("Warm coat", d["outfit"])
        self.assertIn("feels like -2°", d["summary"])

    def test_rain_start_time_and_amount(self):
        pts = hours(6)
        for p in pts[7:]:  # from 14:00
            p["rain"], p["rain_prob"] = 0.5, 80
        d = summarise_day(pts)
        self.assertEqual(d["rain_from"], "14:00")
        self.assertIn("rain likely from 14:00", d["summary"])

    def test_ice_risk_near_zero_with_precipitation(self):
        d = summarise_day(hours(0, rain=0.2, prob=60))
        self.assertIn("Ice risk", d["flags"])
        self.assertIn("Shoes with good grip", d["outfit"])

    def test_no_ice_when_dry_and_above_zero(self):
        self.assertNotIn("Ice risk", summarise_day(hours(3))["flags"])

    def test_heavy_rain_and_storm(self):
        d = summarise_day(hours(8, rain=1.0, prob=90, gust=22))
        self.assertIn("Heavy rain", d["flags"])
        self.assertIn("Storm", d["flags"])

    def test_estonian_reflector_in_the_dark(self):
        d = summarise_day(hours(2), country_code="EE", sunset="15:51")
        self.assertTrue(any("Reflector" in i and "15:51" in i for i in d["outfit"]))
        self.assertFalse(any("Reflector" in i for i in summarise_day(hours(2), "PT", "17:20")["outfit"]))

    def test_no_probability_outside_nordics(self):
        d = summarise_day(hours(18, rain=0.5, prob=None))
        self.assertIsNone(d["rain_chance"])
        self.assertIn("(8.0 mm)", d["summary"])
        self.assertNotIn("%", d["summary"])
        self.assertIn("Umbrella or waterproof", d["outfit"])

    def test_night_only_points_give_nothing(self):
        self.assertIsNone(summarise_day(hours(5, start=0, end=6)))


class Outlook(unittest.TestCase):
    def block(self, h, tmin, tmax, rain=0.0, symbol="cloudy"):
        return {"local": f"2026-12-04T{h:02d}:00:00+00:00", "temp": tmin, "feels": tmin - 2, "tmin": tmin, "tmax": tmax,
                "rain": rain, "rain_prob": None, "gust": 5, "symbol": symbol}

    def test_outlook_is_labelled_and_uses_the_range(self):
        d = outlook_day([self.block(6, 12, 15), self.block(12, 14, 18, rain=2.0)])
        self.assertTrue(d["outlook"])
        self.assertTrue(d["summary"].startswith("Outlook (less precise): 12° to 18°"))
        self.assertIn("Umbrella or waterproof", d["outfit"])

    def test_cold_snowy_outlook_flags_ice(self):
        d = outlook_day([self.block(6, -3, 0, rain=1.0, symbol="snow")])
        self.assertIn("Ice risk", d["flags"])
        self.assertIn("Snow", d["flags"])

    def test_no_blocks(self):
        self.assertIsNone(outlook_day([]))



class KnownPlaces(unittest.TestCase):
    def test_home_city_needs_no_lookup(self):
        p = known_place("Tallinn")
        self.assertEqual((p["country_code"], p["timezone"]), ("EE", "Europe/Tallinn"))
        self.assertTrue(p["yr_url"].endswith("/2-588409"))

    def test_case_accents_and_country_suffix(self):
        self.assertEqual(known_place("malaga")["name"], "Málaga")
        self.assertEqual(known_place("Tartu, Estonia")["country_code"], "EE")

    def test_unknown_city_falls_back(self):
        self.assertIsNone(known_place("Nowhereville"))

    def test_table_is_sane(self):
        import json
        from weather import PLACES_FILE
        with open(PLACES_FILE, encoding="utf-8") as f:
            places = json.load(f)
        for k, r in places.items():
            self.assertTrue(-90 <= r["lat"] <= 90 and -180 <= r["lon"] <= 180, k)
            self.assertIn("/", r["timezone"], k)



class Blocked(unittest.TestCase):
    """Regression: a blocked domain must say what to fix, not crash with a traceback."""

    def error_for(self, exc):
        with mock.patch("urllib.request.urlopen", side_effect=exc):
            with self.assertRaises(SystemExit) as cm:
                weather._get("https://api.met.no/weatherapi/locationforecast/2.0/complete?lat=1&lon=1")
        return json.loads(str(cm.exception.code))["error"]

    def test_403_names_the_domain_and_the_fix(self):
        msg = self.error_for(urllib.error.HTTPError("u", 403, "Forbidden", {}, None))
        self.assertTrue(msg.startswith("Blocked:"))
        self.assertIn("api.met.no", msg)
        self.assertIn("allowed domains", msg)

    def test_unreachable_host_is_blocked_too(self):
        msg = self.error_for(urllib.error.URLError("Name or service not known"))
        self.assertTrue(msg.startswith("Blocked: can't reach api.met.no"))

    def test_other_http_errors_are_not_called_blocked(self):
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError("u", 500, "x", {}, None)):
            with self.assertRaises(urllib.error.HTTPError):
                weather._get("https://api.met.no/x")


if __name__ == "__main__":
    unittest.main()
