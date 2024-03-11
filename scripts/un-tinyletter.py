import re
import pathlib

tl_pat = r"https?://tinyletter.com/data-is-plural/letters/data-is-plural-(\d{4}-\d{2}-\d{2})-edition"

def rewrite_internal_link(m):
    match = re.search(tl_pat, m.group(0))
    date  = match.group(1)
    if date == "2016-02-23":
        date = "2016-02-24"
    return f"https://www.data-is-plural.com/archive/{date}-edition"

def main():
    paths = pathlib.Path("editions/").glob("*.md")
    for path in paths:
        with path.open() as f:
            content = f.read()
        rewritten = re.sub(tl_pat, rewrite_internal_link, content)
        with path.open("w") as f:
            f.write(rewritten)

if __name__ == "__main__":
    main()
