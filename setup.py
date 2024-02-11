from setuptools import setup, find_packages


setup(
    name="Attribute Parser",
    version="0.1",
    packages=find_packages(exclude=["tests*"]),
    license="MIT",
    description="Some way to parse attributes.",
    long_description=open("readme.md").read(),
    url="https://github.com/Thewildweb/attribute_parser.git",
    author="Erik Meijer",
    author_email="erik@datadepartment.io",
)
