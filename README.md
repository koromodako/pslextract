# PSLExtract

Name parser based on [Public Suffix List](https://publicsuffix.org/) (a.k.a. PSL). 

This package is an alternative to [publicsuffixlist](https://pypi.org/project/publicsuffixlist/).

## Setup

Use [Python virtual environements](https://docs.python.org/3/library/venv.html) for the best experience.

```bash
# in a venv
pip install pslextract
```

## CLI Usage

```bash
# Fetch latest Public Suffix List version, use -h for help
pslfetch
# Parse latest Public Suffix List (after pslfetch), use -h for help
pslparse
# Process FQDNs
names=(
    raw.githubusercontent.com
    koromodako.github.io
    github.com
)
pslextract ${names[@]} | jq
```
```json
{
  "name": "raw.githubusercontent.com",
  "prefix": "",
  "public_suffix": "githubusercontent.com",
  "private_suffix": "raw.githubusercontent.com"
}
{
  "name": "koromodako.github.io",
  "prefix": "",
  "public_suffix": "github.io",
  "private_suffix": "koromodako.github.io"
}
{
  "name": "github.com",
  "prefix": "",
  "public_suffix": "com",
  "private_suffix": "github.com"
}
```

## API Usage

```python
from dataclasses import asdict
from json import dumps

from pslextract import (
    DEFAULT_JSON_FILE,
    DEFAULT_RAW_FILE,
    PSLIndex,
    json_dumps,
    psl_create_index,
    psl_extract,
    psl_fetch,
)

NAMES = (
    'example.com',                # a valid Name
    'sub.example.com',            # a valid Name
    'sub.api.gov.uk',             # a valid Name
    ''                            # an invalid Name (empty string)
    '127.0.0.1',                  # an invalid Name (IPv4 address)
    'fe80::1010:1e8f:3f57:fe54',  # an invalid Name (IPv6 address)
    'subexamplecom',              # an invalid Name (missing dots)
    'sub....example.com',         # an invalid Name (empty components)
    'co.uk',                      # an invalid Name (suffix only)
    'sub.sld.notavalidtld',       # an invalid Name (unknown tld)
)


def main():
    if not DEFAULT_JSON_FILE.is_file():
        if not DEFAULT_RAW_FILE.is_file():
            psl_fetch()
        index = psl_create_index()
        index.to_json_file()
    index = PSLIndex.from_json_file()
    for name in NAMES:
        name = psl_extract(index, name)
        if not name:
            continue
        dct = {'name': name.value}
        dct.update(asdict(name))
        print(json_dumps(dct))


if __name__ == '__main__':
    main()
```
