#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import click
from tempfile import NamedTemporaryFile
from email.generator import Generator

from poast import DATE_TYPE, message_queue
from poast.config import Config


@click.group()
def cli():
    pass


@cli.command()
@click.argument('start', type=DATE_TYPE)
@click.argument('end', type=DATE_TYPE)
@click.argument('dir', type=click.Path(exists=True))
def queue(start, end, dir, cfg_var="POAST_CONFIG"):
    cfg = Config.from_envvar(cfg_var)
    for msg in message_queue(start, end, cfg):
        with NamedTemporaryFile(dir=dir, delete=False, prefix='') as fp:
            Generator(fp).flatten(msg)


if __name__ == '__main__':
    cli()
