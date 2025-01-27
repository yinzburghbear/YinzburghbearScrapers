import json
import re
import sys
from typing import Any

from AlgoliaAPI.AlgoliaAPI import (
  ScrapedMovie,
  gallery_from_fragment,
  gallery_from_url,
  movie_from_url,
  performer_from_fragment,
  performer_from_url,
  performer_search,
  scene_from_fragment,
  scene_from_url,
  scene_search
)

from py_common import log
from py_common.types import ScrapedScene
from py_common.util import scraper_args

channel_name_map = {
    "AnalPlaytime": "Anal Acrobats",
    "Anal Trixxx": "AnalTriXXX",
    "Jonni Darkko ": "Jonni Darkko XXX",    # trailing space is in the API
    "Le Wood": "LeWood",
    "Secret Crush ": "Secret Crush",    # trailing space is in the API
}
"""
This map just contains overrides when using a channel name as the studio
"""

serie_name_map = {
    "TransPlaytime": "TS Playground",
    "XXXmailed": "Blackmailed",
}
"""
Each serie_name found in the logic should have a key-value here
"""

site_map = {
    "christophclarkonline": "Christoph Clark Online",
    "christophsbignaturaltits": "Christoph's Big Natural Tits",
    "gapingangels": "Gaping Angels",
    "iloveblackshemales": "I Love Black Shemales",
    "jakemalone": "Jake Malone",
    "johnleslie": "John Leslie",
    "lexingtonsteele": "Lexington Steele",
    "nachovidalhardcore": "Nacho Vidal Hardcore",
    "pansexualx": "PansexualX",
    "pantypops": "Panty Pops",
    "povblowjobs": "POV Blowjobs",
    "roccosiffredi": "Rocco Siffredi",
    "sheplayswithhercock": "She Plays With Her Cock",
    "strapattackers": "Strap Attackers",
    "tittycreampies": "Titty Creampies",
    "transgressivexxx": "TransgressiveXXX",
    "tsfactor": "TS Factor",
}
"""
Each site found in the logic should have a key-value here
"""

def determine_studio(api_object: dict[str, Any]) -> str | None:
    available_on_site = api_object.get("availableOnSite", [])
    main_channel_name = api_object.get("mainChannel", {}).get("name")
    serie_name = api_object.get("serie_name")
    log.debug(
        f"available_on_site: {available_on_site}, "
        f"main_channel_name: {main_channel_name}, "
        f"serie_name: {serie_name}, "
    )

    # determine studio override with custom logic
    # steps through from api_scene["availableOnSite"], and picks the first match
    if site_match := next(
        (site for site in available_on_site if site in site_map.keys()),
        None
    ):
        return site_map.get(site_match, site_match)
    elif serie_name in serie_name_map.keys():
        return serie_name_map.get(serie_name, serie_name)
    elif main_channel_name in [
        "AnalPlaytime",
        "Anal Trixxx",
        "Buttman",
        "Cock Choking Sluts",
        "Euro Angels",
        "Jonni Darkko ",    # trailing space is in the API
        "Le Wood",
        "Secret Crush ",    # trailing space is in the API
        "Transsexual Angel",
    ]:
        return channel_name_map.get(main_channel_name, main_channel_name)
    elif director_match := next(
        (item for item in [
            "Joey Silvera",
            "Mike Adriano",
        ] if item in [c.get("name") for c in api_object.get("channels")]),
        None
    ):
        return director_match
    elif movie_desc := api_object.get("movie_desc"):
        if "BAM Visions" in movie_desc:
            return "BAM Visions"
    return None


def fix_ts_trans_find_replace(text: str) -> str | None:
    """
    At some point in time, there was a mass find-replace performed that replaced
    all occurrences of "TS" or "ts" with "Trans".

    The problem with this is that it replaced every match naively, resulting in
    these examples:
    - tits -> tiTrans
    - hits -> hiTrans

    This regex sub should undo those changes, but leave the intended change:
    - TS -> Trans
    """
    if text:
        return re.sub(r"(?<=[a-z])Trans", "ts", text)
    return None


def postprocess_scene(scene: ScrapedScene, api_scene: dict[str, Any]) -> ScrapedScene:
    if studio_override := determine_studio(api_scene):
        scene["studio"] = { "name": studio_override }

    if description_fixed := fix_ts_trans_find_replace(api_scene.get("description")):
        scene["details"] = description_fixed

    return scene


def postprocess_movie(movie: ScrapedMovie, api_movie: dict[str, Any]) -> ScrapedMovie:
    if studio_override := determine_studio(api_movie):
        movie["studio"] = { "name": studio_override }

    if synopsis := movie.get("synopsis"):
        movie["synopsis"] = fix_ts_trans_find_replace(synopsis)
    
    return movie


if __name__ == "__main__":
    op, args = scraper_args()
    result = None

    log.debug(f"args: {args}")
    match op, args:
        case "gallery-by-url", {"url": url} if url:
            result = gallery_from_url(url)
        case "gallery-by-fragment", args:
            sites = args.pop("extra")
            result = gallery_from_fragment(args, sites)
        case "scene-by-url", {"url": url} if url:
            result = scene_from_url(url, postprocess=postprocess_scene)
        case "scene-by-name", {"name": name, "extra": extra} if name and extra:
            sites = extra
            result = scene_search(name, sites, postprocess=postprocess_scene)
        case "scene-by-fragment" | "scene-by-query-fragment", args:
            sites = args.pop("extra")
            result = scene_from_fragment(args, sites, postprocess=postprocess_scene)
        case "performer-by-url", {"url": url}:
            result = performer_from_url(url)
        case "performer-by-fragment", args:
            result = performer_from_fragment(args)
        case "performer-by-name", {"name": name, "extra": extra} if name and extra:
            sites = extra
            result = performer_search(name, sites)
        case "movie-by-url", {"url": url} if url:
            result = movie_from_url(url, postprocess=postprocess_movie)
        case _:
            log.error(f"Operation: {op}, arguments: {json.dumps(args)}")
            sys.exit(1)

    print(json.dumps(result))
