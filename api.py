import sys
import os
import json
import time
import urllib.error
import urllib.request
import urllib.parse
from typing import *

use_cache: bool = True
user_agent: dict[str, str] = {"User-Agent": "Item Atlas Scraper/1.0 (+https://github.com/Ku-Tadao/runelite-wiki-scraper)"}


def fetch_json(url: str, attempts: int = 3) -> any:
    """
    fetch_json retries network and API errors with backoff, then
    raises so a broken run fails instead of hanging or publishing
    partial data
    """
    for attempt in range(attempts):
        print("Grabbing " + url)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=user_agent), timeout=60) as raw:
                js = json.load(raw)
            if "error" not in js:
                return js
            error = js["error"]
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            error = e
        print(f"Attempt {attempt + 1} failed: {error}")
        if attempt < attempts - 1:
            time.sleep(5 * 2 ** attempt)
    raise RuntimeError(f"Giving up on {url}: {error}")


def get_wiki_api(args: dict[str, str], continue_key: str) -> Iterator[any]:
    args["format"] = "json"
    while True:
        url = "https://oldschool.runescape.wiki/api.php?" + urllib.parse.urlencode(args)
        js = fetch_json(url)

        yield js
        if "continue" in js:
            args[continue_key] = js["continue"][continue_key]
        else:
            return


def get_wiki_bucket_api(query: str, order_by: str) -> Iterator[any]:
    args = {"action": "bucket", "format": "json", "query": query}
    offset = 0

    while True:
        args["query"] = f'{query}.limit(500).offset({offset}).orderBy("{order_by}", "asc").run()'
        url = "https://oldschool.runescape.wiki/api.php?" + urllib.parse.urlencode(args) + "&formatversion=2"
        js = fetch_json(url)
        yield js
        if len(js["bucket"]) < 500:
            return
        offset += 500


def query_category(category_name: str) -> dict[str, dict[str, str]]:
    """
    query_category returns a dict of page title to page wikitext
    you can then use mwparserfromhell to parse the wikitext into
    an ast
    """
    cache_file_name = category_name + ".cache.json"
    if use_cache and os.path.isfile(cache_file_name):
        with open(cache_file_name, "r") as fi:
            return json.load(fi)

    pageids = []
    for res in get_wiki_api(
            {
                "action": "query",
                "list": "categorymembers",
                "cmlimit": "500",
                "cmtitle": "Category:" + category_name,
            }, "cmcontinue"):

        for page in res["query"]["categorymembers"]:
            pageids.append(str(page["pageid"]))

    pages = {}
    for i in range(0, len(pageids), 50):
        for res in get_wiki_api(
                {
                    "action": "query",
                    "prop": "revisions|info",
                    "rvprop": "content",
                    "inprop": "url",
                    "pageids": "|".join(pageids[i:i + 50]),
                }, "rvcontinue"):
            for page_id, page in res["query"]["pages"].items():
                pages[page["title"]] = {
                    "page": page["revisions"][0]["*"],
                    "url": page["fullurl"]
                }

    with open(cache_file_name, "w+") as fi:
        json.dump(pages, fi)

    return pages


def bucket_category_production(category_name: str) -> List[dict]:
    """
    bucket_category_production returns a list of all Production JSON
    properties in a given category
    """
    cache_file_name = category_name + "-production" + ".cache.json"
    if use_cache and os.path.isfile(cache_file_name):
        with open(cache_file_name, "r") as fi:
            return json.load(fi)

    items = []
    for res in get_wiki_bucket_api(
            f'bucket("recipe").select("production_json","page_name", "page_name_sub").where({{"Category:{category_name}"}},{{'
            f'"source_template","recipe"}},{{bucket.Not("Category:Pages using information from game APIs or '
            f'cache")}},{{bucket.Not("Category:Interface items")}},{{bucket.Not("Category:Discontinued content")}},'
            f'{{bucket.Not("Category:Pages with null name")}},{{bucket.Not("Category:Jagex moderator items")}},'
            f'{{bucket.Not("Category:Beta items")}})',
            "production_json"):

        if "bucket" in res:
            for item in res["bucket"]:
                recipe_json = json.loads(str(item["production_json"]))
                # recipe_json["page_name"] = item["page_name"]
                recipe_json["page_name_sub"] = item["page_name_sub"]
                items.append(recipe_json)

    with open(cache_file_name, "w+") as fi:
        json.dump(items, fi)

    return items


def bucket_category_drop_sources(category_name: str) -> Dict[str, object]:
    """
    bucket_category_drop_sources returns a list of all Dropsline
    properties in a given category
    """
    cache_file_name = category_name + "-drop-sources" + ".cache.json"
    if use_cache and os.path.isfile(cache_file_name):
        with open(cache_file_name, "r") as fi:
            return json.load(fi)

    drop_items = {}

    query = (f'bucket("dropsline").select("drop_json","item_name").where({{"rare_drop_table", false}}, {{bucket.Not('
             f'"Category:Pages using information from game APIs or cache")}},{{bucket.Not("Category:Interface '
             f'items")}},{{bucket.Not("Category:Discontinued content")}},{{bucket.Not("Category:Pages with null '
             f'name")}},{{bucket.Not("Category:Jagex moderator items")}},{{bucket.Not("Category:Beta items")}})')

    for res in get_wiki_bucket_api(query, "item_name"):
        if "bucket" in res:
            for item in res["bucket"]:
                drop_json = json.loads(str(item["drop_json"]))
                if drop_json["Dropped item"] in drop_items:
                    drop_items[drop_json["Dropped item"]]["results"].append(drop_json)
                else:
                    drop_items[drop_json["Dropped item"]] = {"results": [drop_json]}

    with open(cache_file_name, "w+") as fi:
        json.dump(drop_items, fi)

    return drop_items


def bucket_item_infobox() -> list[dict]:
    """
    bucket_item_infobox returns a list of all Items in the
    infobox_item bucket
    """
    cache_file_name = "items-infobox" + ".cache.json"
    if use_cache and os.path.isfile(cache_file_name):
        with open(cache_file_name, "r") as fi:
            return json.load(fi)

    items = []

    query = (f'bucket("infobox_item").select("page_name", "page_name_sub", "item_name", "version_anchor", '
             f'"default_version", "is_members_only", "tradeable", "examine", "item_id").where({{bucket.Not('
             f'"Category:Pages using information from game APIs or cache")}},{{bucket.Not("Category:Interface '
             f'items")}},{{bucket.Not("Category:Discontinued content")}},{{bucket.Not("Category:Pages with null '
             f'name")}},{{bucket.Not("Category:Jagex moderator items")}},{{bucket.Not("Category:Beta items")}})')

    for res in get_wiki_bucket_api(query, "item_id"):
        if "bucket" in res:
            for item in res["bucket"]:
                if "item_id" in item:
                    items.append(item)

    with open(cache_file_name, "w+") as fi:
        json.dump(items, fi)

    return items


def query_redirects(page_names: list[str], category: str, items: list[dict]) -> dict[str, dict]:
    cache_file_name = "redirects-" + category + ".cache.json"
    mismatch_file_name = "output/redirects-mismatch-" + category + ".json"
    if use_cache and os.path.isfile(cache_file_name):
        with open(cache_file_name, "r") as fi:
            return json.load(fi)

    redirects = {}
    mismatches = {}

    for i in range(0, len(page_names), 50):
        for res in get_wiki_api(
                {
                    "action": "query",
                    "titles": "|".join(page_names[i:i + 50]),
                    "redirects": 1
                }, "rdcontinue"):
            if "redirects" in res["query"]:
                for redirect in res["query"]["redirects"]:
                    obj = {
                        "name": redirect["to"],
                        "version": redirect["tofragment"] if "tofragment" in redirect else None
                    }
                    redirects[redirect["from"]] = obj
                    versions = [i["version"] for i in items if i["group"] == redirect["to"]]

                    if "tofragment" not in redirect or (len(versions) > 0 and redirect["tofragment"] not in versions):
                        mismatches[redirect["from"]] = obj

    with open(cache_file_name, "w+") as fi:
        json.dump(redirects, fi)

    with open(mismatch_file_name, "w+") as fi:
        json.dump(mismatches, fi, indent=2, sort_keys=True)

    return redirects


def query_pages(titles: list[str], cache_name: str) -> dict[str, str]:
    """
    query_pages returns a dict of requested title to page wikitext,
    following redirects. Missing pages are left out.
    """
    cache_file_name = cache_name + ".cache.json"
    if use_cache and os.path.isfile(cache_file_name):
        with open(cache_file_name, "r") as fi:
            return json.load(fi)

    pages = {}
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        # requested title -> final title, through normalization and redirects
        final = {t: t for t in batch}
        texts = {}
        for res in get_wiki_api(
                {
                    "action": "query",
                    "prop": "revisions",
                    "rvprop": "content",
                    "redirects": "1",
                    "titles": "|".join(batch),
                }, "rvcontinue"):
            query = res["query"]
            for hop in query.get("normalized", []) + query.get("redirects", []):
                for t, cur in final.items():
                    if cur == hop["from"]:
                        final[t] = hop["to"]
            for page in query["pages"].values():
                if "revisions" in page:
                    texts[page["title"]] = page["revisions"][0]["*"]
        for t, cur in final.items():
            if cur in texts:
                pages[t] = texts[cur]

    with open(cache_file_name, "w+") as fi:
        json.dump(pages, fi)

    return pages
