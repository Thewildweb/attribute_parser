from setuptools import setup, find_packages


setup(
    name="attribute_parser",
    version="0.3",
    packages=["attributeparser"],
    package_dir={"": "src"},
    license="MIT",
    description="Some way to parse attributes.",
    long_description=open("readme.md").read(),
    url="https://github.com/Thewildweb/attribute_parser.git",
    author="Erik Meijer",
    author_email="erik@datadepartment.io",
)
