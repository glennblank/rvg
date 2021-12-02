#!/usr/bin/env python3.9

import click
import rvg

# ./cli.py --help
# ./cli.py --step

@click.command()
@click.option('--step', is_flag=True, help='Show more details about matching productions')
def cli(step):
    print("Step is true!" if step else "Step is false!")
    rvg.rvg(step)

if __name__ == '__main__':
    cli()
