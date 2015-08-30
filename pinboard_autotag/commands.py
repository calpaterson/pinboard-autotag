from logging import getLogger, INFO, basicConfig
from pathlib import Path
from os.path import expanduser
from contextlib import closing

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import click
import requests
from lxml import html
from lxml.cssselect import CSSSelector

from pinboard_autotag.data import (
    Bookmark,
    BookmarkContents,
    BookmarkTitle,
    BookmarkProblem,
    metadata,
)

logger = getLogger(__name__)

HTTP_TIMEOUT = 20

@click.group()
def cli():
    basicConfig(level=INFO)


@cli.command()
@click.argument("api_token")
def get_bookmarks(api_token):
    Session = ensure_dotfiles()

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

    with closing(Session()) as s:
        for bookmark_url, title in bookmarks:
            bm = Bookmark(href=bookmark_url)
            bm.title = BookmarkTitle(title=title)
            s.add(bm)
        s.commit()


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
    metadata.bind = engine
    metadata.create_all()
    return sessionmaker(bind=metadata.bind)


@cli.command()
def download_links():
    Session = ensure_dotfiles()

    with closing(Session()) as s:
        while True:
            rs = (
                s.query(Bookmark.href)
                .outerjoin(BookmarkContents)
                .outerjoin(BookmarkProblem)
                .filter(BookmarkContents.href.is_(None))
                .filter(BookmarkProblem.href.is_(None))
                .first()
            )
            if rs is None:
                break;
            url = rs[0]
            try:
                response = requests.get(
                    url,
                    timeout=HTTP_TIMEOUT
                )
            except requests.exceptions.RequestException as e:
                logger.exception("{url} timed out after {http_timeout}".format(
                    url=url,
                    http_timeout=HTTP_TIMEOUT
                ))
                s.add(BookmarkProblem(
                    href=url,
                    problem=e.__class__.__name__,
                ))
                s.commit()
                continue
            logger.info("got {status_code} from {url}".format(
                status_code=response.status_code,
                url=url
            ))
            if response.status_code != 200:
                s.add(BookmarkProblem(
                    href=url,
                    problem="HTTP {status_code}".format(
                        status_code=response.status_code
                    )
                ))
                s.commit()
                continue
            s.add(BookmarkContents(
                href=url,
                contents=response.content
            ))
            s.commit()

