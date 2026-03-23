"""pslextract serialization operations"""

from json import JSONDecodeError, dumps, loads
from pathlib import Path

from .logging import get_logger

_LOGGER = get_logger('parse')
DEFAULT_JSON_FILE = Path.home() / '.cache' / 'pslextract' / 'psl.json'

PSLIndexNode = dict[str, 'PSLIndexNode']


def json_dumps(obj):
    """Compact json dumps"""
    return dumps(obj, separators=(',', ':'))


def psl_index_from_json(json_text: str) -> PSLIndexNode:
    """Load from JSON text"""
    try:
        return loads(json_text)
    except JSONDecodeError:
        _LOGGER.exception("invalid json")
    return None


def psl_index_from_json_file(
    json_file: Path = DEFAULT_JSON_FILE,
) -> PSLIndexNode:
    """Load from JSON file"""
    if not json_file.is_file():
        _LOGGER.error("not found or not a regular file: %s", json_file)
        return None
    try:
        json_text = json_file.read_text(encoding='utf-8')
        return psl_index_from_json(json_text)
    except UnicodeDecodeError:
        _LOGGER.exception("unicode decode error!")
    except PermissionError:
        _LOGGER.exception("cannot read %s", json_file)
    return None


def psl_index_to_json(index: PSLIndexNode) -> str:
    """Dump to JSON text"""
    return json_dumps(index)


def psl_index_to_json_file(
    index: PSLIndexNode, json_file: Path = DEFAULT_JSON_FILE
):
    """Dump to JSON file"""
    text = psl_index_to_json(index)
    json_file.write_text(text, encoding='utf-8')
