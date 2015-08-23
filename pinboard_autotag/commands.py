from logging import getLogger, INFO, basicConfig

import click
import requests
from lxml import html
from lxml.cssselect import CSSSelector


logger = getLogger(__name__)


@click.group()
def cli():
    basicConfig(level=INFO)


@cli.command()
@click.argument("api_token")
def get_bookmarks(api_token):
    logger.info("api_token = {api_token}".format(api_token=api_token))
    all_bookmarks = requests.get(
        "https://api.pinboard.in/v1/posts/all?auth_token={api_token}"
        .format(api_token=api_token)
    )
    logger.info("got {status_code} from /all".format(
        status_code=all_bookmarks.status_code))

    tree = html.fromstring(all_bookmarks.content)
    sel = CSSSelector("post")
    bookmarks = {(e.get("href"), e.get("description")) for e in sel(tree)}

    for bookmark_url, title in bookmarks:
        logger.info(title)
