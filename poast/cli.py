# -*- coding: utf-8 -*-
from __future__ import absolute_import

import getpass
import logging
from logging.config import fileConfig
from smtplib import SMTP, SMTP_SSL, SMTPRecipientsRefused
from tempfile import NamedTemporaryFile
from time import sleep

import click

from poast import delivery_queue, messages
from poast.db import collection, engine

try:
    from email.generator import BytesGenerator as Generator
except ImportError:
    from email.generator import Generator


fileConfig('poast/config/logger.ini')
logger = logging.getLogger('poast')


@click.group()
def main():
    pass


@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--mongo', default='mongodb://localhost:27017')
@click.option('--mongo-database', default='oastats')
@click.option('--mongo-collection', default='summary')
@click.option('--people-db', default='sqlite://')
@click.option('--sender', default='oastats@mit.edu')
@click.option('--reply-to', default='oastats@mit.edu')
@click.option('--subject',
              default='Download statistics for your articles in DSpace@MIT')
@click.option('--threshold', default=20, type=int)
def queue(path, mongo, mongo_database, mongo_collection, people_db, sender,
          reply_to, subject, threshold):
    summary = collection(mongo, mongo_database, mongo_collection)
    engine.configure(people_db)
    for msg in messages(summary, sender, reply_to, subject, threshold):
        with NamedTemporaryFile(dir=path, delete=False, prefix='') as fp:
            Generator(fp).flatten(msg)


@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.confirmation_option(prompt='Are you sure you want to send emails?')
@click.option('--username', default=getpass.getuser())
@click.option('--password', prompt=True, hide_input=True)
@click.option('--smtp-host', default='localhost')
@click.option('--smtp-port', default=465, type=int)
@click.option('--ssl/--no-ssl', default=True)
def mail(path, username, password, smtp_host, smtp_port, ssl):
    if not ssl:
        s = SMTP(smtp_host, smtp_port)
    else:
        s = SMTP_SSL(smtp_host, smtp_port)
        try:
            s.login(username, password)
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
