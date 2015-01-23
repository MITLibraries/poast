#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import click
from poast import create_mailer


@click.group()
def cli():
    pass


@cli.command()
def mail():
    mailer = create_mailer()
    mailer.queue_messages()


if __name__ == '__main__':
    cli()