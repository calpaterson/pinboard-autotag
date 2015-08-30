from sqlalchemy import MetaData, Column, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)


class Bookmark(Base):
    __tablename__ = "bookmarks"

    href = Column(Text, primary_key=True)

    title = relationship(
        "BookmarkTitle",
        uselist=False,
        backref=backref("bookmark", uselist=False)
    )

    content_type = relationship(
        "BookmarkContentType",
        uselist=False,
        backref=backref("bookmark", uselist=False)
    )

    tags = relationship(
        "BookmarkTag",
        backref=backref("bookmark", uselist=False)
    )


class BookmarkTitle(Base):
    __tablename__ = "bookmark_titles"

    href = Column(ForeignKey("bookmarks.href"), primary_key=True)
    title = Column(Text, primary_key=True)


class BookmarkTag(Base):
    __tablename__ = "bookmark_tags"

    href = Column(ForeignKey("bookmarks.href"), primary_key=True)
    tag = Column(Text, primary_key=True)


class BookmarkContentType(Base):
    __tablename__ = "bookmark_content_types"

    href = Column(ForeignKey("bookmarks.href"), primary_key=True)
    mimetype = Column(Text, nullable=False)
    character_set = Column(Text, nullable=False)
