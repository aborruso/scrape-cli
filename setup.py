# setup.py
from setuptools import setup
from pathlib import Path

# Leggi il README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="scrape-cli",
    version="1.1.6",
    description="It's a command-line tool to extract HTML elements using an XPath query or CSS3 selector.",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Specifica formato Markdown
    author="Andrea Borruso",
    author_email="aborruso@gmail.com",
    url="https://github.com/aborruso/scrape-cli",
    packages=["scrape_cli"],  # nota: usa underscore invece di trattino
    entry_points={
        'console_scripts': [
            'scrape=scrape_cli.scrape:main',
        ],
    },
    install_requires=[
        "cssselect",
        "lxml",
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
