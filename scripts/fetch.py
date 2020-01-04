#!/usr/bin/env python
import requests
import lxml.html
import pypandoc
import os
import re
from copy import deepcopy
from datetime import datetime

DATE_FIXES = {
    "2016-02-23": "2016-02-24", 
}

def get_edition_urls():
    url = "https://tinyletter.com/data-is-plural/archive"

    html = requests.get(
        url,
        params = {
            "page": 1,
            "recs": 1000,
            "sort": "desc"
        }
    ).content

    dom = lxml.html.fromstring(html)
    dom.make_links_absolute(url)

    links = [ link.attrib["href"]
        for link in dom.cssselect(".message-link") ]

    return links

def clean_md(md):
    md = re.sub(r"^ +", "", md)
    md = re.sub(r"<[^>@]+>", "", md)
    md = re.sub(r"\s*\n\s*\n\s*", "\n\n\n\n", md)
    md = re.sub(r"===\n+", "===\n\n", md)
    md = re.sub(r"\n\n\n\n", "\n\n&nbsp;\n\n", md)
    md = re.sub(r"&nbsp;\s+$", "", md)
    md = re.sub(r"%%LEFTBRACKET%%", "[", md)
    md = re.sub(r"%RIGHTBRACKET%%", "]", md)
    md = md.strip()
    return md

def clean_html(html):
    html = re.sub(r"<strong>\s*</strong>", " ", html)
    html = re.sub(r"<i>\s*</i>", " ", html)
    html = re.sub(r"(<a\b[^>]*>)<i>(.*?)</i></a>", r"<i>\1\2</a></i>", html)
    html = re.sub(r"</i>\s*<i>", r"", html)
    html = re.sub(r"\[", r"%%LEFTBRACKET%%", html)
    html = re.sub(r"\]", r"%RIGHTBRACKET%%", html)
    return html

class Edition:
    def __init__(self, url):
        self.url = url

        raw_url_date = re.search(
            r"(\d{4}-\d{2}-\d{2})-edition",
            url,
        ).group(1)

        self.url_date = DATE_FIXES.get(raw_url_date, raw_url_date)

    def fetch(self):
        self.html = requests.get(self.url).content
        self.dom = lxml.html.fromstring(self.html)
        self.select = self.dom.cssselect
        return self

    @property
    def date(self):
        date_el = self.dom.cssselect("#message-heading .date")[0]
        date_str = date_el.text_content().strip()
        date = datetime.strptime(date_str, "%B %d, %Y")
        better_date_str = date.strftime("%Y-%m-%d")
        return better_date_str

    @property
    def markdown(self):
        dom = deepcopy(self.dom)
        for e in dom.cssselect("small"):
            e.getparent().remove(e)

        h1s = dom.cssselect("h1")
        inner = dom.cssselect(".message-body")
        els = h1s + inner

        msg_html = clean_html(b"\n".join(map(lxml.html.tostring, els)).decode("utf-8"))

        md = pypandoc.convert_text(
            msg_html,
            "markdown_strict",
            format = "html",
            extra_args = [
                "--wrap=none",
            ]
        )

        cleaned = clean_md(md)
        return cleaned

def main():
    urls = get_edition_urls()
    for url in urls:
        ed = Edition(url)
        dest = f"editions/{ed.url_date}.md"
        if os.path.exists(dest):
            continue
        print(ed.url)
        ed.fetch()
        if ed.date != ed.url_date:
            print("!  " + url)
            exit()
        md = ed.markdown
        with open(dest, "w") as f:
            f.write(md)

if __name__ == "__main__":
    main()
