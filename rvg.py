#!/usr/bin/env python3.9

import click
import rvgprocessor

@click.command()
@click.option('--step', '-s', is_flag=True, default=False, help='Show more details about matching productions')
@click.option('--back', '-b', is_flag=True, default=False, help='Show boundary backtracking')
def cli(step,back):
    if step: mode = 1
    elif back: mode = 2
    else: mode = None
    rvgprocessor.rvg(mode)

if __name__ == '__main__':
    cli()
