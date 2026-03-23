"""pslextract parsing operations"""

from argparse import ArgumentParser
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from sys import exit as sys_exit

from .__version__ import version
from .fetch import DEFAULT_RAW_FILE
from .logging import get_logger
from .serialize import DEFAULT_JSON_FILE, PSLIndexNode, psl_index_to_json_file

_LOGGER = get_logger('parse')


def psl_lines_from_raw(raw_file: Path) -> Iterator[str]:
    """Yield preprocessed lines from PSL raw file"""
    with raw_file.open('r', encoding='utf-8') as fobj:
        for line in fobj:
            line = line.strip('.* \n')
            if not line:
                continue
            if line.startswith('//'):
                continue
            yield line


def psl_create_index(raw_file: Path = DEFAULT_RAW_FILE) -> PSLIndexNode:
    """Create index from PSL raw file"""
    index = {}
    for line in psl_lines_from_raw(raw_file):
        pointer = index
        components = line.split('.')
        while components:
            last = components.pop()
            pointer = pointer.setdefault(last, {})
    return index


def app():
    """pslparse entrypoint"""
    _LOGGER.info("pslparse %s", version)
    parser = ArgumentParser()
    parser.add_argument(
        '--raw-file',
        type=Path,
        default=DEFAULT_RAW_FILE,
        help="Raw Public Suffix List file",
    )
    parser.add_argument(
        '--json-file',
        type=Path,
        default=DEFAULT_JSON_FILE,
        help="JSON file used to store Public Suffix List index",
    )
    parser.add_argument(
        '--erase', action='store_true', help="Erase JSON file if exists"
    )
    args = parser.parse_args()
    if args.json_file.is_file() and not args.erase:
        _LOGGER.warning("existing file found: %s", args.json_file)
        _LOGGER.warning("add --erase argument to force replacement")
        sys_exit(1)
    if not args.raw_file.is_file():
        _LOGGER.warning("file not found: %s", args.raw_file)
        sys_exit(2)
    start = datetime.now()
    _LOGGER.info("build index...")
    index = psl_create_index(args.raw_file)
    _LOGGER.info("writing index to %s ...", args.json_file)
    psl_index_to_json_file(index, args.json_file)
    _LOGGER.info("operation took %s", datetime.now() - start)
    sys_exit(0)
