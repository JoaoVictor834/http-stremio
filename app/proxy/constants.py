import os

# static list of hosts
STATIC_ALLOWED_HOSTS = [
    "www.imdb.com",
    "live.metahub.space",
    "images.metahub.space",
    "episodes.metahub.space",
]

# dinamically updated inside utils.py by `add_proxy_to_hls_parts`
M3U8_PARTS_HOSTS = []

# conjunction of STATIC_ALLOWED_HOSTS, M3U8_PARTS_HOSTS, and other hosts related to different scrapers
# dinamically updated inside utils.py by `update_allowed_hosts`
ALLOWED_HOSTS = []

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

HLS_CONTENT_TYPE_HEADERS = [
    "application/vnd.apple.mpegURL",
    "application/x-mpegURL",
    "audio/mpegurl",
    "audio/x-mpegurl",
    "text/plain",
]
