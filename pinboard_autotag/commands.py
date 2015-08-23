from logging import getLogger, INFO, basicConfig

import click


logger = getLogger(__name__)


@click.group()
def cli():
    basicConfig(level=INFO)


@cli.command()
@click.argument("api_token")
def get_bookmarks(api_token):
    logger.info("api_token = {api_token}".format(api_token=api_token))
