#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import click
from tempfile import NamedTemporaryFile
from email.generator import Generator
from smtplib import SMTP_SSL, SMTPRecipientsRefused
from time import sleep
import logging
from logging.config import fileConfig

from poast import message_queue, delivery_queue
from poast.config import Config


fileConfig('poast/config/logger.ini')
logger = logging.getLogger('poast')


@click.group()
def cli():
    pass


@cli.command()
@click.argument('dir', type=click.Path(exists=True))
def queue(dir, cfg_var="POAST_CONFIG"):
    cfg = Config.from_envvar(cfg_var)
    for msg in message_queue(cfg):
        with NamedTemporaryFile(dir=dir, delete=False, prefix='') as fp:
            Generator(fp).flatten(msg)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.confirmation_option(prompt='Are you sure you want to send emails?')
@click.password_option()
def mail(path, password, cfg_var="POAST_CONFIG"):
    cfg = Config.from_envvar(cfg_var)
    s = SMTP_SSL(cfg['SMTP_HOST'], cfg['SMTP_PORT'])
    try:
        s.login(cfg['SMTP_USER'], password)
    except:
        s.quit()
        raise
    try:
        for msg in delivery_queue(path):
            receiver = msg['To']
            sender = msg['From']
            try:
                s.sendmail(sender, receiver, msg.as_string())
                logger.info('Mail sent: %s' % receiver)
            except SMTPRecipientsRefused:
                logger.warning('%s address refused' % receiver)
            sleep(0.1)
    finally:
        s.quit()


if __name__ == '__main__':
    cli()
