#!/usr/bin/env python3.9

import click
import rvg

@click.command()
@click.option('--step', '-s', is_flag=True, default=False, help='Show more details about matching productions')
def cli(step):
    print("Step is true!" if step else "Step is false!")
    rvg.rvg(step)

if __name__ == '__main__':
    cli()
