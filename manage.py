import subprocess
import signal
import sys
import time

import uvicorn

from src.app.main import app


def run_uvicorn(port: int, ssl: bool = False):
    cmd = [
        "uvicorn",
        "main:app",
        "--host",
        "0.0.0.0",
        "--port",
        str(port),
    ]
    if ssl:
        cmd.extend(["--ssl-keyfile", "localhost.key", "--ssl-certfile", "localhost.crt"])
    return subprocess.Popen(cmd)


if __name__ == "__main__":
    try:
        scheme = sys.argv[1]
    except IndexError:
        scheme = ""

    if scheme and (scheme not in ("http", "https")):
        exit(f"'{scheme}' in not a valid value for scheme, use 'http' or 'https' to specify a scheme or ommit it to use both")

    match scheme:
        case "https":
            # start https server on port 6222
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=6222,
                ssl_keyfile="localhost.key",
                ssl_certfile="localhost.crt",
            )

        case "http":
            # start http server on port 6223
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=6223,
            )

        case _:
            # start http server on port 6223
            http_process = run_uvicorn(6223)

            # start https server on port 6222
            https_process = run_uvicorn(6222, ssl=True)

            # handle Ctrl+C gracefully
            def shutdown(signum, frame):
                print("\nShutting down servers...")
                http_process.terminate()
                https_process.terminate()
                sys.exit(0)

            signal.signal(signal.SIGINT, shutdown)

            # keep the main process alive
            try:
                while True:
                    time.sleep(999)
            except KeyboardInterrupt:
                shutdown(None, None)
