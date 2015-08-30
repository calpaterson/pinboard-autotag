from setuptools import setup

config = {
    "description": "A program that auto-tags pinboard bookmarks",
    "author": "pinboard-autotagger",
    "url": "https://github.com/calpaterson/pinboard-autotag",
    "author_email": "cal@calpaterson.com",
    "version": "0.0",
    "install_requires": [
        "pytz",
        "SQLAlchemy>=1.0.0",
        "Click>=5.1",
        "requests==2.7.0",
        "lxml==3.4.4",
        "cssselect==0.9.1",
    ],
    "packages": ["pinboard_autotag"],
    "scripts": [],
    "name": "PinboardAutotag",
    "entry_points": {
        "console_scripts": [
            "pinboard_autotag = pinboard_autotag.commands:cli",
        ]
    }
}

setup(**config)
