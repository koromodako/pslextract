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
# Explore Public Suffix List index using jq from top level to sub levels
jq '.uk.gov' ${HOME}/.cache/pslextract/psl.json
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
  "domain": "raw.githubusercontent.com",
  "suffix": "githubusercontent.com"
}
{
  "name": "koromodako.github.io",
  "prefix": "",
  "domain": "koromodako.github.io",
  "suffix": "github.io"
}
{
  "name": "github.com",
  "prefix": "",
  "domain": "github.com",
  "suffix": "com"
}
```

## API Usage

```python
from dataclasses import asdict
from json import dumps

from pslextract import (
    DEFAULT_JSON_FILE,
    DEFAULT_RAW_FILE,
    psl_create_index,
    psl_extract,
    psl_fetch,
    psl_index_from_json_file,
    psl_index_to_json_file,
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
        psl_index_to_json_file(index)
    index = psl_index_from_json_file()
    for name in NAMES:
        name = psl_extract(index, name)
        if not name:
            continue
        print(dumps(asdict(name)))


if __name__ == '__main__':
    main()
```
