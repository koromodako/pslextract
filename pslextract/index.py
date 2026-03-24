"""pslextract serialization operations"""

from dataclasses import dataclass, field
from functools import cached_property
from json import JSONDecodeError, dumps, loads
from pathlib import Path

from .logging import get_logger

_LOGGER = get_logger('parse')
DEFAULT_JSON_FILE = Path.home() / '.cache' / 'pslextract' / 'psl.json'


def json_dumps(obj):
    """Compact json dumps"""
    return dumps(obj, separators=(',', ':'))


@dataclass(kw_only=True)
class Name:
    """Name"""

    prefix: str
    public_suffix: str
    private_suffix: str

    @cached_property
    def value(self) -> str:
        """Original value"""
        return '.'.join(filter(None, [self.prefix, self.private_suffix]))


@dataclass(kw_only=True)
class PSLIndex:
    """PSL Index"""

    suffixes: set[str] = field(default_factory=set)
    wildcard: set[str] = field(default_factory=set)
    excluded: set[str] = field(default_factory=set)

    @classmethod
    def from_json(cls, json_text: str):
        """Load from JSON text"""
        try:
            dct = loads(json_text)
        except JSONDecodeError:
            _LOGGER.exception("invalid json")
            return None
        return cls(
            suffixes=set(dct['suffixes']),
            wildcard=set(dct['wildcard']),
            excluded=set(dct['excluded']),
        )

    @classmethod
    def from_json_file(cls, json_file: Path = DEFAULT_JSON_FILE):
        """Load from JSON file"""
        if not json_file.is_file():
            _LOGGER.error("not found or not a regular file: %s", json_file)
            return None
        try:
            json_text = json_file.read_text(encoding='utf-8')
            return cls.from_json(json_text)
        except UnicodeDecodeError:
            _LOGGER.exception("unicode decode error!")
        except PermissionError:
            _LOGGER.exception("cannot read %s", json_file)
        return None

    def to_json(self) -> str:
        """Dump to JSON text"""
        return json_dumps(
            {
                'suffixes': list(self.suffixes),
                'wildcard': list(self.wildcard),
                'excluded': list(self.excluded),
            }
        )

    def to_json_file(self, json_file: Path = DEFAULT_JSON_FILE):
        """Dump to JSON file"""
        text = self.to_json()
        json_file.write_text(text, encoding='utf-8')

    def add(self, public_suffix: str):
        """Add a public suffix to PSL index"""
        if public_suffix.startswith('*.'):
            self.wildcard.add(public_suffix[2:])
            return
        if public_suffix.startswith('!'):
            self.excluded.add(public_suffix[1:])
            return
        self.suffixes.add(public_suffix)

    def parse(self, name: str) -> Name | None:
        """Parse given name using PSL index"""
        components = name.split('.')
        suffix_l = []
        while components:
            current_comp = components.pop()
            suffix_l.insert(0, current_comp)
            suffix_s = '.'.join(suffix_l)
            suffix_s_prev = '.'.join(suffix_l[1:])
            # shortcut if excluded
            if suffix_s in self.excluded:
                return Name(
                    prefix='.'.join(components),
                    public_suffix=suffix_s_prev,
                    private_suffix=suffix_s,
                )
            # not excluded, check if matches a wildcard
            if suffix_s_prev in self.wildcard:
                if not components:
                    return None
                return Name(
                    prefix='.'.join(components[:-1]),
                    public_suffix=suffix_s,
                    private_suffix='.'.join([components[-1]] + suffix_l),
                )
            # not excluded, not matching wilcard, still public ?
            if suffix_s in self.suffixes:
                continue
            # private part found
            return Name(
                prefix='.'.join(components),
                public_suffix=suffix_s_prev,
                private_suffix=suffix_s,
            )
        return None
