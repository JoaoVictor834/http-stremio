class StremioStream:
    def __init__(self, name: str, title: str, url: str, not_web_ready: bool = False, headers: dict | None = None):
        self.name = name
        self.title = title
        self.url = url
        self.not_web_ready = not_web_ready
        if headers is not None:
            self.headers = headers
        else:
            self.headers = {}

    def to_dict(self):
        return {
            "name": self.name,
            "title": self.title,
            "url": self.url,
            "behaviorHints": {
                "notWebReady": self.not_web_ready,
                "proxyHeaders": self.headers,
            },
        }


class StremioStreamManager:
    def __init__(self):
        self.streams = []

    def add_stream(self, name: str, title: str, url: str, not_web_ready: bool = False, headers: dict | None = None):
        stream = StremioStream(name, title, url, not_web_ready, headers)
        self.streams.append(stream)

    def to_list(self):
        return [stream.to_dict() for stream in self.streams]

    def to_dict(self):
        return {"streams": self.to_list()}


if __name__ == "__main__":
    streams = StremioStreamManager()
    streams.add_stream("name", "title", "https://example.com")
    streams.add_stream("name1", "title1", "https://example1.com")

    from pprint import pprint

    pprint(streams.to_dict())
