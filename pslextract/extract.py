"""pslextract extraction operations"""

from argparse import ArgumentParser
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import datetime
from functools import cached_property
from pathlib import Path
from sys import exit as sys_exit

from .__version__ import version
from .logging import get_logger
from .parse import DEFAULT_JSON_FILE
from .serialize import PSLIndexNode, json_dumps, psl_index_from_json_file

_LOGGER = get_logger('extract')


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


def psl_validate_name(index: PSLIndexNode, name: str) -> bool:
    """Determine if given name is valid"""
    if not name:
        _LOGGER.warning("invalid name (empty string)")
        return False
    if '.' not in name:
        _LOGGER.warning("invalid name (missing dot): '%s'", name)
        return False
    if '..' in name:
        _LOGGER.warning("invalid name (contiguous dots): '%s'", name)
        return False
    _, tld = name.rsplit('.', 1)
    if tld not in index:
        _LOGGER.warning("invalid name (unknown tld): '%s'", name)
        return False
    return True


def psl_extract(
    index: PSLIndexNode, name: str, validate: bool = True
) -> Name | None:
    """Perform extraction for given name"""
    if validate and not psl_validate_name(index, name):
        return None
    suffix = []
    domain = []
    pointer = index
    components = name.split('.')
    while components:
        current = components.pop()
        pointer = pointer.get(current)
        if isinstance(pointer, dict):
            suffix.append(current)
            continue
        domain = [current] + suffix[::-1]
        break
    return Name(
        prefix='.'.join(components),
        domain='.'.join(domain),
        suffix='.'.join(suffix[::-1]),
    )


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
    index = psl_index_from_json_file(args.json_file)
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
