"""pslextract extraction operations"""

from argparse import ArgumentParser
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import datetime
from functools import cached_property
from pathlib import Path
from re import compile as regexp
from sys import exit as sys_exit

from .__version__ import version
from .logging import get_logger
from .parse import DEFAULT_JSON_FILE
from .index import PSLIndex, json_dumps

_LOGGER = get_logger('extract')
_PATTERN = regexp(r'([\w\-]+\.)+(?P<tld>[\w\-]+)')


@dataclass(kw_only=True)
class Name:
    """Name"""

    prefix: str
    domain: str
    suffix: str

    @cached_property
    def value(self) -> str:
        """Original value"""
        return '.'.join(filter(None, [self.prefix, self.domain]))


def psl_validate_name(index: PSLIndex, name: str) -> bool:
    """Determine if given name is valid"""
    if not name:
        _LOGGER.warning("invalid name (empty string)")
        return False
    match = _PATTERN.fullmatch(name)
    if not match:
        _LOGGER.warning("invalid name (unexpected pattern): '%s'", name)
        return False
    tld = match.group('tld')
    if tld not in index.suffixes:
        _LOGGER.warning("invalid name (unknown tld): '%s'", name)
        return False
    return True


def psl_extract(
    index: PSLIndex, name: str, validate: bool = True
) -> Name | None:
    """Perform extraction for given name"""
    if validate and not psl_validate_name(index, name):
        return None
    return index.parse(name)


def _parse_name_list(name_list: list[str]) -> Iterator[str]:
    for name in name_list:
        filepath = Path(name)
        if not filepath.is_file():
            yield name
            continue
        with filepath.open('r', encoding='utf-8') as fobj:
            for line in fobj:
                if '#' in line:
                    line = line.split('#', 1)[0]
                if '//' in line:
                    line = line.split('//', 1)[0]
                line = line.strip()
                if not line:
                    continue
                yield line


def app():
    """pslextract entrypoint"""
    _LOGGER.info("pslextract %s", version)
    parser = ArgumentParser()
    parser.add_argument(
        '--json-file',
        type=Path,
        default=DEFAULT_JSON_FILE,
        help="JSON file used to store Public Suffix List index",
    )
    parser.add_argument('name_list', nargs='+', metavar='name', help="")
    args = parser.parse_args()
    if not args.json_file.is_file():
        _LOGGER.warning("file not found: %s", args.raw_file)
        sys_exit(1)
    start = datetime.now()
    _LOGGER.info("reading index from %s ...", args.json_file)
    index = PSLIndex.from_json_file(args.json_file)
    _LOGGER.info("extractings ...")
    for name in _parse_name_list(args.name_list):
        name = psl_extract(index, name)
        if not name:
            continue
        dct = {'name': name.value}
        dct.update(asdict(name))
        print(json_dumps(dct))
    _LOGGER.info("operation took %s", datetime.now() - start)
    sys_exit(0)
