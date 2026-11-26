#!/usr/bin/env python3
"""Forecast and what to wear, from MET Norway (the source behind yr.no).

The numbers come straight from api.met.no; the clothing advice comes from fixed
rules below, so no AI rewords the forecast. Standard library only.

Usage:
  python3 tools/weather.py --place "London" --days 2
  python3 tools/weather.py --place "Lisbon" --from 2026-12-04 --days 3
Prints one JSON object: {"place": {...}, "days": [{date, summary, outfit, flags, ...}]}

MET Norway asks clients to identify themselves; set WEATHER_USER_AGENT
(e.g. "my-weather-agent/1.0 you@example.com") to include your contact.
"""
import argparse
import json
import os
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

UA = os.environ.get("WEATHER_USER_AGENT", "sardon-steadfast-weather/1.0 (+https://github.com/sumanreddy89/sardon-starter)")
FORECAST = "https://api.met.no/weatherapi/locationforecast/2.0/complete?lat={lat:.4f}&lon={lon:.4f}"
SUN = "https://api.met.no/weatherapi/sunrise/3.0/sun?lat={lat:.4f}&lon={lon:.4f}&date={d}&offset={off}"
GEOCODE = "https://geocoding-api.open-meteo.com/v1/search?count=1&language=en&name={q}"

# Parts of the day you're likely to be outside, local time [start, end)
PERIODS = [("Morning", 7, 11), ("Midday", 11, 15), ("Afternoon", 15, 19), ("Evening", 19, 23)]
WAKING = (7, 23)

# Rain and wind thresholds
RAIN_PROB = 50          # % chance in an hour that makes a waterproof worth it
RAIN_MM = 1.0           # mm over waking hours
HEAVY_MM_DAY = 8.0
HEAVY_MM_HOUR = 3.0
WINDY_GUST = 12.0       # m/s: an umbrella turns inside out, wind cuts through knits
STORM_GUST = 20.0


# ---------- data fetching ----------

def blocked_message(host, code=None):
    """Plain words for a refused or unreachable host: the owner has to change a setting."""
    why = (f"{host} refused the request ({code})" if code else f"can't reach {host}")
    return (f"Blocked: {why}. Add {host} to the allowed domains of this routine's cloud "
            f"environment on claude.ai; if it's already there, set weather.user_agent in Config "
            f"to include your contact details.")


def _get(url):
    host = urllib.parse.urlparse(url).hostname
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 407):
            raise SystemExit(json.dumps({"error": blocked_message(host, e.code)}))
        raise
    except urllib.error.URLError:
        raise SystemExit(json.dumps({"error": blocked_message(host)}))


PLACES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "places.json")


def _key(name):
    """Case- and accent-insensitive key: "Málaga" and "malaga" match."""
    name = unicodedata.normalize("NFKD", name.split(",")[0].strip().lower())
    return "".join(c for c in name if not unicodedata.combining(c))


def known_place(name, path=PLACES_FILE):
    """Look the city up in places.json so everyday runs need only api.met.no."""
    try:
        with open(path, encoding="utf-8") as fh:
            table = json.load(fh)
    except (OSError, ValueError):
        return None
    want = _key(name)
    for k, r in table.items():
        if want in (_key(k), _key(r["name"])):
            return {"name": r["name"], "country": r["country"], "country_code": r["country_code"],
                    "lat": r["lat"], "lon": r["lon"], "timezone": r["timezone"],
                    "yr_url": f"https://www.yr.no/en/forecast/daily-table/2-{r['id']}"}
    return None


def find_place(name):
    """Built-in table first; the geocoding site only for cities not in it."""
    return known_place(name) or geocode(name)


def geocode(name):
    res = _get(GEOCODE.format(q=urllib.parse.quote(name))).get("results") or []
    if not res:
        raise SystemExit(json.dumps({"error": f"place not found: {name}"}))
    r = res[0]
    return {"name": r["name"], "country": r.get("country", ""), "country_code": r.get("country_code", ""),
            "lat": r["latitude"], "lon": r["longitude"], "timezone": r.get("timezone", "UTC"),
            "yr_url": f"https://www.yr.no/en/forecast/daily-table/2-{r['id']}"}


def hourly(place):
    """Hourly points in local time: list of dicts."""
    data = _get(FORECAST.format(lat=place["lat"], lon=place["lon"]))
    tz = ZoneInfo(place["timezone"])
    out, six = [], []
    for t in data["properties"]["timeseries"]:
        nxt = t["data"].get("next_1_hours")
        if not nxt:
            n6 = t["data"].get("next_6_hours")
            if n6:  # beyond the hourly range: 6-hour blocks, used only for a labelled outlook
                local = datetime.fromisoformat(t["time"].replace("Z", "+00:00")).astimezone(tz)
                inst = t["data"]["instant"]["details"]
                six.append({"local": local.isoformat(), "temp": inst.get("air_temperature"),
                            "feels": inst.get("apparent_air_temperature", inst.get("air_temperature")),
                            "tmin": n6["details"].get("air_temperature_min"), "tmax": n6["details"].get("air_temperature_max"),
                            "rain": n6["details"].get("precipitation_amount", 0) or 0,
                            "rain_prob": n6["details"].get("probability_of_precipitation"),
                            "gust": inst.get("wind_speed_of_gust", inst.get("wind_speed")) or 0,
                            "symbol": n6["summary"]["symbol_code"]})
            continue
        inst = t["data"]["instant"]["details"]
        local = datetime.fromisoformat(t["time"].replace("Z", "+00:00")).astimezone(tz)
        out.append({
            "local": local.isoformat(),
            "temp": inst.get("air_temperature"),
            "feels": inst.get("apparent_air_temperature", inst.get("air_temperature")),
            "temp_lo": inst.get("air_temperature_percentile_10"),
            "temp_hi": inst.get("air_temperature_percentile_90"),
            "gust": inst.get("wind_speed_of_gust", inst.get("wind_speed")),
            "wind": inst.get("wind_speed"),
            "uv": inst.get("ultraviolet_index_clear_sky", 0) or 0,
            "rain": nxt["details"].get("precipitation_amount", 0) or 0,
            "rain_prob": nxt["details"].get("probability_of_precipitation"),  # None outside the Nordic area
            "symbol": nxt["summary"]["symbol_code"],
        })
    return out, six, data["properties"]["meta"]["updated_at"]


def sun(place, d):
    off = datetime.now(ZoneInfo(place["timezone"])).strftime("%z")
    off = off[:3] + ":" + off[3:]
    try:
        p = _get(SUN.format(lat=place["lat"], lon=place["lon"], d=d.isoformat(), off=off))["properties"]
        return (p.get("sunrise") or {}).get("time", "")[11:16], (p.get("sunset") or {}).get("time", "")[11:16]
    except Exception:
        return "", ""


# ---------- pure logic (tested) ----------

def summarise_day(points, country_code="", sunset=""):
    """points: that day's hourly dicts (local). Returns the day summary with outfit and flags."""
    awake = [p for p in points if WAKING[0] <= int(p["local"][11:13]) < WAKING[1]]
    if not awake:
        return None
    temps = [p["temp"] for p in awake]
    feels = [p["feels"] for p in awake]
    rain_total = round(sum(p["rain"] for p in awake), 1)
    probs = [p["rain_prob"] for p in awake if p["rain_prob"] is not None]
    max_prob = max(probs) if probs else None
    max_gust = max(p["gust"] or 0 for p in awake)
    max_uv = max(p["uv"] for p in awake)
    symbols = {p["symbol"].split("_")[0] for p in awake}
    snowy = any("snow" in s or "sleet" in s for s in symbols)
    wet_hours = [p for p in awake if (p["rain_prob"] or 0) >= RAIN_PROB or p["rain"] >= 0.3]
    rain_from = wet_hours[0]["local"][11:16] if wet_hours else ""

    flags = []
    near_zero = any(-3 <= p["temp"] <= 1 for p in points)
    if near_zero and (rain_total > 0.2 or snowy or any(p["temp"] <= 0 for p in points) and rain_total > 0):
        flags.append("Ice risk")
    if rain_total >= HEAVY_MM_DAY or any(p["rain"] >= HEAVY_MM_HOUR for p in awake):
        flags.append("Heavy rain" if not snowy else "Heavy snow")
    if max_gust >= STORM_GUST:
        flags.append("Storm")
    elif max_gust >= WINDY_GUST:
        flags.append("Windy")
    if snowy and "Heavy snow" not in flags:
        flags.append("Snow")

    outfit = outfit_for(min(feels), rain_total, max_prob or 0, max_gust, snowy, "Ice risk" in flags, max_uv)
    if country_code.upper() == "EE" and sunset and sunset < "18:00":
        outfit.append(f"Reflector (helkur): dark from {sunset}")

    periods = []
    for name, a, b in PERIODS:
        ps = [p for p in awake if a <= int(p["local"][11:13]) < b]
        if ps:
            pp = [p["rain_prob"] for p in ps if p["rain_prob"] is not None]
            periods.append({"name": name, "temp": round(sum(p["temp"] for p in ps) / len(ps)),
                            "feels": round(min(p["feels"] for p in ps)),
                            "rain_prob": round(max(pp)) if pp else None,
                            "rain": round(sum(p["rain"] for p in ps), 1),
                            "symbol": max(ps, key=lambda p: (p["rain_prob"] or 0, p["rain"]))["symbol"]})

    lo, hi = round(min(temps)), round(max(temps))
    parts = [f"{lo}° to {hi}°, feels like {round(min(feels))}°"]
    if wet_hours:
        kind = "snow" if snowy else "rain"
        chance = f"{round(max_prob)}%, " if max_prob is not None else ""
        parts.append(f"{kind} likely from {rain_from} ({chance}{rain_total} mm)")
    else:
        parts.append("dry")
    if max_gust >= WINDY_GUST:
        parts.append(f"gusts to {round(max_gust)} m/s")
    return {
        "low": lo, "high": hi, "feels_min": round(min(feels)),
        "uncertainty": round(max((p["temp_hi"] or p["temp"]) - (p["temp_lo"] or p["temp"]) for p in awake), 1),
        "rain_mm": rain_total, "rain_chance": round(max_prob) if max_prob is not None else None, "rain_from": rain_from,
        "gust_max": round(max_gust, 1), "flags": flags, "outfit": outfit,
        "periods": periods, "summary": "; ".join(parts),
    }


def outlook_day(blocks, country_code="", sunset=""):
    """Less precise summary from 6-hour blocks (days 3-9)."""
    if not blocks:
        return None
    lows = [b["tmin"] if b["tmin"] is not None else b["temp"] for b in blocks]
    highs = [b["tmax"] if b["tmax"] is not None else b["temp"] for b in blocks]
    feels = min(min(b["feels"] for b in blocks), min(lows))
    rain = round(sum(b["rain"] for b in blocks), 1)
    probs = [b["rain_prob"] for b in blocks if b["rain_prob"] is not None]
    gust = max(b["gust"] for b in blocks)
    snowy = any("snow" in b["symbol"] or "sleet" in b["symbol"] for b in blocks)
    icy = min(lows) <= 1 and (rain > 0.2 or snowy)
    outfit = outfit_for(feels, rain, max(probs) if probs else 0, gust, snowy, icy, 0)
    if country_code.upper() == "EE" and sunset and sunset < "18:00":
        outfit.append(f"Reflector (helkur): dark from {sunset}")
    flags = (["Ice risk"] if icy else []) + (["Snow"] if snowy else []) + (["Windy"] if gust >= WINDY_GUST else [])
    wet = rain >= RAIN_MM or (probs and max(probs) >= RAIN_PROB)
    summary = (f"Outlook (less precise): {round(min(lows))}° to {round(max(highs))}°; "
               + (f"{'snow' if snowy else 'rain'} likely ({rain} mm)" if wet else "mostly dry"))
    return {"low": round(min(lows)), "high": round(max(highs)), "feels_min": round(feels), "uncertainty": None,
            "rain_mm": rain, "rain_chance": round(max(probs)) if probs else None, "rain_from": "",
            "gust_max": round(gust, 1), "flags": flags, "outfit": outfit, "periods": [], "summary": summary,
            "outlook": True}


def outfit_for(feels_min, rain_mm, rain_prob, gust, snowy, icy, uv):
    """Clothing from the coldest 'feels like' while you're out, plus rain, wind, snow and ice."""
    if feels_min <= -15:
        items = ["Heavy down coat", "Thermal base layer", "Warm hat", "Scarf", "Insulated gloves", "Winter boots"]
    elif feels_min <= -5:
        items = ["Winter coat", "Warm mid-layer", "Hat", "Gloves", "Scarf", "Winter boots"]
    elif feels_min <= 2:
        items = ["Warm coat", "Sweater", "Hat", "Gloves"]
    elif feels_min <= 8:
        items = ["Medium jacket", "Sweater or hoodie"]
    elif feels_min <= 14:
        items = ["Light jacket", "Long sleeves"]
    elif feels_min <= 20:
        items = ["Long sleeves or a light layer"]
    else:
        items = ["T-shirt"]
    wet = rain_mm >= RAIN_MM or rain_prob >= RAIN_PROB
    if wet and not snowy:
        items.append("Waterproof shell with a hood" if gust >= WINDY_GUST else "Umbrella or waterproof")
    if snowy and "Winter boots" not in items:
        items.append("Waterproof boots")
    if icy:
        items.append("Shoes with good grip")
    if gust >= WINDY_GUST and not any("coat" in i.lower() or "shell" in i.lower() for i in items):
        items.append("Windproof outer layer")
    if uv >= 3:
        items.append("Sunglasses and sunscreen")
    return items


def by_day(points):
    days = {}
    for p in points:
        days.setdefault(p["local"][:10], []).append(p)
    return days


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--place", required=True)
    ap.add_argument("--from", dest="start", help="YYYY-MM-DD (default: today at the place)")
    ap.add_argument("--days", type=int, default=2)
    ap.add_argument("--kind", choices=["home", "trip"], default="home",
                    help="home: first day is Today, then Tomorrow; trip: every day is Trip")
    a = ap.parse_args(argv)
    place = find_place(a.place)
    points, six, updated = hourly(place)
    tz = ZoneInfo(place["timezone"])
    start = date.fromisoformat(a.start) if a.start else datetime.now(tz).date()
    grouped, grouped6 = by_day(points), by_day(six)
    days = []
    for i in range(a.days):
        d = start + timedelta(days=i)
        pts = grouped.get(d.isoformat())
        sunrise, sunset = sun(place, d)
        s = summarise_day(pts, place["country_code"], sunset) if pts else None
        if not s:
            s = outlook_day(grouped6.get(d.isoformat(), []), place["country_code"], sunset)
        if not s:
            days.append({"date": d.isoformat(), "available": False,
                         "summary": "Detailed forecast doesn't cover the daytime yet; check again closer to the day"})
            continue
        s.update({"date": d.isoformat(), "available": True, "sunrise": sunrise, "sunset": sunset})
        days.append(s)
    rows = [notion_row(place, d, i, a.kind, updated) for i, d in enumerate(days)]
    print(json.dumps({"place": place, "forecast_updated": updated, "source": "MET Norway (yr.no)",
                      "days": days, "notion_rows": rows}, ensure_ascii=False))


def notion_row(place, d, i, kind, updated):
    """The exact properties for the Weather table, so the agent copies instead of retyping."""
    day = date.fromisoformat(d["date"])
    k = "Trip" if kind == "trip" else ("Today" if i == 0 else "Tomorrow")
    props = {"Day": f"{place['name']} · {day.strftime('%a')} {day.day} {day.strftime('%b')}",
             "Place": place["name"], "date:Date:start": d["date"], "date:Date:is_datetime": 0, "Kind": k,
             "Summary": d["summary"], "Yr": place["yr_url"],
             "date:Updated:start": updated, "date:Updated:is_datetime": 1}
    if d.get("available"):
        props.update({
            "Outfit": ", ".join(d["outfit"]), "Flags": json.dumps(d["flags"]),
            "Low": d["low"], "High": d["high"], "Feels": d["feels_min"],
            "Rain chance": d["rain_chance"], "Rain mm": d["rain_mm"], "Rain from": d["rain_from"],
            "Gust": d["gust_max"], "Sun": f"{d['sunrise']}–{d['sunset']}" if d.get("sunrise") else "",
            "Periods": "; ".join(f"{p['name']} {p['temp']}° (feels {p['feels']}°)" + (f", rain {p['rain_prob']}%" if p['rain_prob'] is not None else (f", {p['rain']} mm" if p['rain'] else ", dry")) for p in d["periods"]),
        })
    return props


if __name__ == "__main__":
    main()
