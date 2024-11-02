from setuptools import setup

setup(
    name="scrape-cli",
    version="0.1",
    description="It's a command-line tool to extract HTML elements using an XPath query or CSS3 selector.",
    author="Il tuo nome",
    packages=["scrape-cli"],
    install_requires=["cssselect", "lxml"],
)
