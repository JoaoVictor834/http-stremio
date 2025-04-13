class VideoPageParsningError(Exception):
    """Failed to extract video url from video page"""


class ServerFormsParsingError(Exception):
    """Could not extract download page url from serverforms html"""


class DownloadPageParsingError(Exception):
    """Could not extract download page url from serverforms html"""
