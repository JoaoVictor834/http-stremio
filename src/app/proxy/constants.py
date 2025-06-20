import os

from src.scrapers import pobreflix, redecanais, warezcdn

# conjunction of raw hosts strings defined here and on each scraper
ALLOWED_HOSTS = [
    "www.imdb.com",
    "live.metahub.space",
    "images.metahub.space",
    "episodes.metahub.space",
    *redecanais.ALLOWED_HOSTS,
    *warezcdn.ALLOWED_HOSTS,
]

# list of regular expressions that match urls used by scrapers
ALLOWED_REGEXS = [
    *redecanais.ALLOWED_REGEXS,
    *warezcdn.ALLOWED_REGEXS,
]

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

HLS_CONTENT_TYPE_HEADERS = [
    "application/vnd.apple.mpegURL",
    "application/x-mpegURL",
    "audio/mpegurl",
    "audio/x-mpegurl",
    "text/plain",
]
