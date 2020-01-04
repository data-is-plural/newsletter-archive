#!/usr/bin/env python
from feedgen.feed import FeedGenerator
import pypandoc
import lxml.html
import pytz
import datetime
from glob import glob
import re
import sys

FEED_SETTINGS = {
    "link": {
        "href": "https://tinyletter.com/data-is-plural",
        "rel": "alternate",
    },
    "id": "https://tinyletter.com/data-is-plural",
    "title": "Data Is Plural",
    "description": "A weekly newsletter of useful/curious datasets.",
    "author": {
        "name": "Jeremy Singer-Vine",
        "email": "jsvine@gmail.com",
    },
    "generator": "https://github.com/data-is-plural/newsletter-archive",
}

tz = pytz.timezone("US/Eastern")

def call_dict_as_methods(obj, d):
    for k, v in d.items():
        setter = getattr(obj, k)
        if isinstance(v, dict):
            setter(**v)
        else:
            setter(v)

def create_item(path):
    text = open(path).read()

    date_str = path[-13:-3]
    date_tup = tuple(map(int, date_str.split("-")))
    date = tz.localize(
        datetime.datetime(*(date_tup + (8, 0, 0)))
    )

    html = pypandoc.convert_text(
        "\n".join(text.strip().split("\n")[3:]),
        "html",
        format = "markdown_strict",
    )

    return {
        "link": {
            "href": f"http://tinyletter.com/data-is-plural/letters/data-is-plural-{date_str}-edition"
        },
        "title": text.strip().split("\n")[0],
        "guid": f"dip-{date_str}",
        "published": date,
        "updated": date,
        "summary": re.search(r"\*(.+?)\*\s*\n", text).group(1),
        "content": {
            "content": html,
            "type": "CDATA",
        },
    }


def build():
    feed = FeedGenerator()
    call_dict_as_methods(feed, FEED_SETTINGS)

    paths = sorted(glob("editions/*.md"), reverse = True)[:10]

    for i, path in enumerate(paths):
        entry = feed.add_entry(order = "append")
        data = create_item(path)
        call_dict_as_methods(entry, data)
        if i == 0:
            feed.updated(data["updated"])

    return feed

def main():
    if len(sys.argv) > 1:
        fmt = sys.argv[1]
    else:
        fmt = "rss"
    feed = build()
    writer = getattr(feed, f"{fmt}_str")
    output = writer(pretty = True)
    sys.stdout.buffer.write(output)

if __name__ == "__main__":
    main() 
