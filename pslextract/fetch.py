"""pslextract fetching operations"""

from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from sys import exit as sys_exit
from urllib.request import ProxyHandler, build_opener, install_opener, urlopen

from .__version__ import version
from .logging import get_logger

_LOGGER = get_logger('fetch')
DEFAULT_URL = 'https://publicsuffix.org/list/public_suffix_list.dat'
DEFAULT_PROXY = None
DEFAULT_RAW_FILE = Path.home() / '.cache' / 'pslextract' / 'psl.dat'
DEFAULT_CHUNKSIZE = 5 * 1024 * 1024


def psl_fetch(
    raw_file: Path = DEFAULT_RAW_FILE,
    url: str = DEFAULT_URL,
    proxy: str | None = DEFAULT_PROXY,
    chunksize: int = DEFAULT_CHUNKSIZE,
):
    """Download Public Suffix List and store it in raw_file"""
    chunksize = max(4096, chunksize)
    if proxy:
        _LOGGER.info("using proxy %s", proxy)
        proxy_handler = ProxyHandler({'http': proxy, 'https': proxy})
        opener = build_opener(proxy_handler)
        install_opener(opener)
    _LOGGER.info("writing to %s ...", raw_file)
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    with raw_file.open('wb') as fobj:
        _LOGGER.info("fetching %s using chunk size %d ...", url, chunksize)
        with urlopen(url) as response:
            size = int(response.headers['Content-Length'])
            _LOGGER.info("status %d (size=%d)", response.status, size)
            while size > 0:
                chunk = response.read(chunksize)
                fobj.write(chunk)
                size -= len(chunk)
        fobj.flush()
    _LOGGER.info("done fetching %s", url)


def app():
    """pslfetch entrypoint"""
    _LOGGER.info("pslfetch %s", version)
    parser = ArgumentParser()
    parser.add_argument(
        '--raw-file',
        type=Path,
        default=DEFAULT_RAW_FILE,
        help="Raw Public Suffix List file",
    )
    parser.add_argument(
        '--url', default=DEFAULT_URL, help="Public Suffix List URL"
    )
    parser.add_argument(
        '--proxy', default=DEFAULT_PROXY, help="Proxy used to fetch"
    )
    parser.add_argument(
        '--chunksize',
        type=int,
        default=DEFAULT_CHUNKSIZE,
        help="Download chunk size",
    )
    parser.add_argument(
        '--erase', action='store_true', help="Erase raw file if exists"
    )
    args = parser.parse_args()
    if args.raw_file.is_file() and not args.erase:
        _LOGGER.warning("existing file found: %s", args.raw_file)
        _LOGGER.warning("add --erase argument to force replacement")
        sys_exit(1)
    start = datetime.now()
    psl_fetch(
        args.raw_file,
        url=args.url,
        proxy=args.proxy,
        chunksize=args.chunksize,
    )
    _LOGGER.info("operation took %s", datetime.now() - start)
    sys_exit(0)
