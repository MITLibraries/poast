#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import click

from poast import DATE_TYPE, message_queue
from poast.config import Config


@click.group()
def cli():
    pass


@cli.command()
@click.argument('start', type=DATE_TYPE)
@click.argument('end', type=DATE_TYPE)
def mail(start, end, cfg_var="POAST_CONFIG"):
    cfg = Config.from_envvar(cfg_var)
    queue = message_queue(start, end, cfg)


if __name__ == '__main__':
    cli()
