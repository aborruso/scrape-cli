from setuptools import setup

setup(
    name="scrape-cli",
    version="1.1",
    description="It's a command-line tool to extract HTML elements using an XPath query or CSS3 selector.",
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
        "lxml"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
