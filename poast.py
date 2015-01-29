#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import click
from poast import create_mailer, DATE_TYPE


@click.group()
def cli():
    pass


@cli.command()
@click.argument('start', type=DATE_TYPE)
@click.argument('end', type=DATE_TYPE)
def mail(start, end):
    mailer = create_mailer(start, end)
    mailer.queue_messages()


if __name__ == '__main__':
    cli()