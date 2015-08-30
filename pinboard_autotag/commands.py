from logging import getLogger, INFO, basicConfig
from pathlib import Path
from os.path import expanduser

from sqlalchemy import create_engine
import click
import requests
from lxml import html
from lxml.cssselect import CSSSelector

from pinboard_autotag.data import metadata

logger = getLogger(__name__)


@click.group()
def cli():
    basicConfig(level=INFO)


@cli.command()
@click.argument("api_token")
def get_bookmarks(api_token):
    engine = ensure_dotfiles()

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


@cli.command()
def ensure_dotfiles():
    dotdir = Path(expanduser("~")) / Path(".pinboard_autotag/")
    if not dotdir.exists():
        dotdir.mkdir()
        logger.info("created {dotdir}".format(dotdir=dotdir))

    db_location = (
        "sqlite:///{db_location}"
        .format(db_location=dotdir / Path("database.db"))
    )
    logger.info("db_location = " + db_location)
    engine = create_engine(db_location)
    logger.info("engine = " + str(engine))
    metadata.bind=engine
    metadata.create_all()
