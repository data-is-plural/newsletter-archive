.PHONY: rss

rss:
	python scripts/rss.py rss > feeds/dip.rss
	python scripts/rss.py atom > feeds/dip.atom
