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


fileConfig('poast/logging.ini')
logger = logging.getLogger('poast')


@click.group()
@click.version_option()
def main():
    pass


@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--mongo', default='mongodb://localhost:27017',
              help="MongoDB connection URI.")
@click.option('--mongo-database', default='oastats',
              help="Name of OAStats Mongo database. Defaults to oastats.")
@click.option('--mongo-collection', default='summary',
              help="Name of OAStats Mongo collection. Defaults to summary.")
@click.option('--people-db', default='sqlite://',
              help="SQLAlchemy connection string for data warehouse view.")
@click.option('--sender', default='oastats@mit.edu',
              help="Email address to set as From. Default is oastats@mit.edu.")
@click.option('--reply-to', default='oastats@mit.edu',
              help="Email address to set as Reply-To. Default is oastats@mit.edu.")
@click.option('--subject',
              default='Download statistics for your articles in DSpace@MIT',
              help="Subject line for email message. Defaults to 'Download statistics for your articles in DSpace@MIT'")
@click.option('--threshold', default=20, type=int,
              help="Download count threshold below which an email will not be generated for an author. Default is 20.")
def queue(path, mongo, mongo_database, mongo_collection, people_db, sender,
          reply_to, subject, threshold):
    """Generate email messages.

    This will generate email messages for authors contained in the OAStats Mongo database and serialize them to the directory specified by PATH. The author's first name, last name and email address are taken from the data warehouse view. Note that this does not send the emails, it just writes them to files which can be sent later using the poast mail subcommand.

    The --threshold option can be used to filter out those authors who don't have enough downloads. This is calculated by subtracting an author's total number of papers from their total downloads and comparing to the threshold.
    """
    summary = collection(mongo, mongo_database, mongo_collection)
    engine.configure(people_db)
    for msg in messages(summary, sender, reply_to, subject, threshold):
        with NamedTemporaryFile(dir=path, delete=False, prefix='') as fp:
            Generator(fp).flatten(msg)


@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.confirmation_option(prompt='Are you sure you want to send emails?')
@click.option('--username', default=getpass.getuser(),
              help="Username for smtp server. Default is current user.")
@click.option('--password', prompt=True, hide_input=True)
@click.option('--smtp-host', default='localhost',
              help="Defaults to localhost.")
@click.option('--smtp-port', default=465, type=int, help="Defaults to 465.")
@click.option('--ssl/--no-ssl', default=True,
              help="Use SSL when connecting to the SMTP server. The default is to use SSL.")
def mail(path, username, password, smtp_host, smtp_port, ssl):
    """Send email messages in PATH.

    This will recursively search through PATH and attempt to send all email
    messages it finds. It assumes every file it encounters is an email message.
    """
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
