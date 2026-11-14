#!/usr/bin/env python3
"""Preview the portfolio from any working directory, without reusing a stale server."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import sys
import threading
import webbrowser

SITE = Path(__file__).resolve().parents[1] / 'docs'


def check_site():
    for relative in ('index.html', 'work/index.html', 'assets/styles.css', 'assets/app.js'):
        if not (SITE / relative).is_file():
            raise FileNotFoundError(f'Missing website file: {SITE / relative}')
    handler = SimpleHTTPRequestHandler.__new__(SimpleHTTPRequestHandler)
    handler.directory = str(SITE)
    assert Path(handler.translate_path('/')).resolve() == SITE.resolve()
    assert Path(handler.translate_path('/index.html')).resolve() == SITE / 'index.html'
    assert Path(handler.translate_path('/work/')).resolve() == SITE / 'work'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check preview paths without opening a socket.')
    args = parser.parse_args()
    check_site()
    if args.check:
        print(f'Preview paths verified: {SITE}')
        return
    # An OS-assigned port avoids accidentally opening an unrelated or stale preview.
    with ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(SITE))) as server:
        url = f'http://127.0.0.1:{server.server_port}/'
        print(f'Patrick Cabral portfolio: {url}', flush=True)
        print('Keep this window open. Press Control+C to stop the preview.', flush=True)
        threading.Timer(0.3, lambda: webbrowser.open(url)).start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nPreview stopped.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, AssertionError) as error:
        print(f'Could not start the preview: {error}', file=sys.stderr)
        sys.exit(1)
