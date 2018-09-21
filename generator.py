#!/usr/bin/env python3
# coding: UTF-8

from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from io import TextIOWrapper
from typing import Dict, List, Tuple

MIN_PYTHON = (3, 7)


@dataclass(frozen=True)
class Entry:
    timeout: int
    concurrency: int
    requests: int

    @classmethod
    def from_dict(cls, json_dict: Dict) -> Entry:
        return Entry(json_dict['timeout'], json_dict['concurrency'], json_dict['requests'])

    def to_dict(self) -> Dict[str, int]:
        return self.__dict__


@dataclass(frozen=True)
class Script:
    url: str
    entries: Tuple[Entry, ...]

    @classmethod
    def from_dict(cls, json_dict: Dict) -> Script:
        return Script(json_dict['url'], entries=tuple(Entry.from_dict(e) for e in json_dict['entries']))

    def to_dict(self) -> Dict:
        return dict(
                url=self.url,
                entries=[entry.to_dict() for entry in self.entries]
        )


def generate_script(url: str, duration: int, alpha: float, maximum_concurrency: int, timeout_range: range) -> Script:
    entries: List[Entry] = list()

    while duration > 0:
        timeout: int = random.choice(timeout_range)
        concurrency: int = int(random.paretovariate(alpha))

        if concurrency > maximum_concurrency:
            concurrency = maximum_concurrency

        entries.append(Entry(timeout, concurrency, 20000))

        duration -= timeout

    return Script(url, tuple(entries))


def main():
    parser = argparse.ArgumentParser(description='Auto load generator of ab (apache benchmark)')
    parser.add_argument('url', type=str, help='URL to access')
    parser.add_argument('dest_path', type=argparse.FileType('w'), nargs='?', default='script.json',
                        help='the location of the file where the script will be stored (default: script.json)')
    parser.add_argument('-a', '--alpha', type=float, default=0.3,
                        help='the shape parameter of Pareto distribution (default: 0.3)')
    parser.add_argument('-d', '--duration', type=int, default=60,
                        help='total time (second) of experiment (default: 60)')
    parser.add_argument('-m', '--maximum-concurrency', type=int, default=1000,
                        help='maximum concurrency limit (default: 1000)')

    args = parser.parse_args()

    dest_path: TextIOWrapper = args.dest_path
    alpha: float = args.alpha
    url: str = args.url
    duration: int = args.duration
    maximum_concurrency: int = args.maximum_concurrency

    script: Script = generate_script(url, duration, alpha, maximum_concurrency, range(1, 3))
    json.dump(script.to_dict(), dest_path)
    dest_path.close()


if __name__ == '__main__':
    if sys.version_info < MIN_PYTHON:
        sys.exit('Python {}.{} or later is required.\n'.format(*MIN_PYTHON))

    main()
