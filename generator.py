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


def _calc_approximated_requests(duration: float, concurrency: int) -> int:
    # FIXME: hard coded
    if 0 < concurrency <= 8:
        ret = (concurrency * 37.142857143 + 50) * duration
    elif 8 < concurrency <= 16:
        ret = ((concurrency - 8) * 5 + 310) * duration
    elif 16 < concurrency <= 170:
        ret = ((concurrency - 16) * -1.160714286 + 350) * duration
    else:
        ret = concurrency * duration

    return max(int(ret), concurrency)


def generate_script(url: str, duration: int, alpha: float, maximum_concurrency: int) -> Script:
    entries: List[Entry] = list()

    while duration > 0:
        timeout: int = int(random.uniform(1, 5))
        concurrency: int = min(int(10 ** random.expovariate(alpha)), maximum_concurrency)
        requests = _calc_approximated_requests(timeout, concurrency)

        entries.append(Entry(timeout, concurrency, requests))

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

    script: Script = generate_script(url, duration, alpha, maximum_concurrency)
    json.dump(script.to_dict(), dest_path)
    dest_path.close()


if __name__ == '__main__':
    if sys.version_info < MIN_PYTHON:
        sys.exit('Python {}.{} or later is required.\n'.format(*MIN_PYTHON))

    main()
