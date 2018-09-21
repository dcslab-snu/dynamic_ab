#!/usr/bin/env python3
# coding: UTF-8

import argparse
import asyncio
import json
import math
import os
import sys
import time
from itertools import chain
from typing import List, Tuple

import aiofiles

from generator import Script, generate_script

MIN_PYTHON = (3, 7)


async def _run_ab(url: str, concurrency: int, timeout: int, requests: int, verbose: bool) -> str:
    output_file = f'{time.time_ns()}.tsv'
    std = asyncio.subprocess.PIPE if verbose else asyncio.subprocess.DEVNULL

    print('ab', '-g', output_file, '-n', str(requests), '-t', str(timeout), '-c', str(concurrency), url)
    proc = await asyncio.create_subprocess_exec('ab', '-g', output_file, '-n', str(requests),
                                                '-t', str(timeout), '-c', str(concurrency), url,
                                                stdout=std, stderr=std)
    await proc.communicate()

    return output_file


async def _parse_tsv(file_path: str) -> Tuple[int, ...]:
    async with aiofiles.open(file_path) as afp:
        head_arr = (await afp.readline()).split('\t')
        ttime_idx = head_arr.index('ttime')

        return tuple(int(line.split('\t')[ttime_idx]) for line in await afp.readlines())


async def _store_csv_result(latencies: List[int]) -> None:
    size = len(latencies)

    async with aiofiles.open('result.csv', 'w') as afp:
        await afp.write('Percentage served,Time in ms\n')

        for per in range(100):
            idx = math.ceil(size * per / 100)

            await afp.write(f'{per},{latencies[idx]}\n')

        await afp.write(f'100,{latencies[-1]}\n')


async def _interpret(script: Script, verbose: bool) -> None:
    url = script.url

    result_files: List[str] = list()

    for entry in script.entries:
        output_file: str = await _run_ab(url, entry.concurrency, entry.timeout, entry.requests, verbose)
        result_files.append(output_file)

    latencies_list: List[Tuple[int, ...]] = await asyncio.gather(*(_parse_tsv(file_path) for file_path in result_files))
    latencies: List[int, ...] = sorted(chain(*latencies_list))

    await _store_csv_result(latencies)

    for file_path in result_files:
        os.remove(file_path)


def main() -> None:
    parser = argparse.ArgumentParser(description='ab (apache benchmark) with auto load generator')
    parser.add_argument('-v', '--verbose', action='store_true', help='print more detail log')

    sub_parser = parser.add_subparsers(dest='command', help='sub-command help')

    interpret_cmd = sub_parser.add_parser('i', help='read a stored script (json type) and interpret it')
    interpret_cmd.add_argument('script_path', type=argparse.FileType('r'),
                               help='the location of the file where the script is stored')

    generate_cmd = sub_parser.add_parser('g', help='generate script in runtime with arguments and interpret it')
    generate_cmd.add_argument('url', type=str, help='URL to access')
    generate_cmd.add_argument('-a', '--alpha', type=float, default=0.3,
                              help='the shape parameter of Pareto distribution (default: 0.3)')
    generate_cmd.add_argument('-d', '--duration', required=True, type=int, help='total time (second) of experiment')
    generate_cmd.add_argument('-o', '--output', type=str, default=None,
                              help='The location of the file where the script will be stored')

    args = parser.parse_args()

    verbose: bool = args.verbose
    command: str = args.command

    if command == 'i':
        with args.script_path as fp:
            json_dict = json.load(fp)

        script = Script.from_dict(json_dict)

    elif command == 'g':
        script = generate_script(args.url, args.duration, args.alpha, range(1, 3))

        if args.output is not None:
            with open(args.output, 'w') as fp:
                json.dump(script.to_dict(), fp)

    else:
        raise NotImplementedError(f'unknown command : {command}')

    asyncio.run(_interpret(script, verbose))


if __name__ == '__main__':
    if sys.version_info < MIN_PYTHON:
        sys.exit('Python {}.{} or later is required.\n'.format(*MIN_PYTHON))

    main()
