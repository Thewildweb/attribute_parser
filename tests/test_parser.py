import pytest

from src.attribute_parser import Attribute
from src.parse_attribute import parse_attributes
from .example_parsers import KamerParser, HuurParser, OppervlakteParser, WaarborgParser


def test_parser():
    """Basic test for the KamerParser"""

    Attribute(
        key="Kamers",
        value="3 kamers",
    )

    parser = KamerParser(
        attribute=Attribute(
            key="Kamers",
            value="3 kamers",
        ),
        tokens=["3", "kamers"],
    )

    assert parser.test_attribute()
    for match in parser.parse():
        assert match.key == "kamer"
        assert match.value == 3


def test_parser_mulitple_values():
    """Test for the KamerParser with multiple values."""

    attribute = Attribute(
        value="3 kamers, 2 slaapkamers",
    )

    parser = KamerParser(
        attribute=attribute,
        tokens=attribute.value.split(),
    )

    assert parser.test_attribute()
    matches = list(parser.parse())
    assert len(matches) == 2

    assert matches[0].key == "kamer"
    assert matches[0].value == 3

    assert matches[1].key == "slaapkamer"
    assert matches[1].value == 2


def test_parser_that_fails_test():
    """Test for the Parser that fails the test."""
    attribute = Attribute(key="Huur", value="€ 1.200 /mnd")

    parser = KamerParser(
        attribute=attribute,
        tokens=attribute.value.split(),
    )

    assert not parser.test_attribute()


def test_huurprijs_parser():
    """Test for huurprijzen."""
    huur_attribute_1 = Attribute(key="Prijs", value="€ 1.200 /mnd")
    huur_attribute_2 = Attribute(
        key="Huurprijs", value="€ 2.650 per maand (servicekosten onbekend)"
    )

    parser = HuurParser(
        attribute=huur_attribute_1,
        tokens=huur_attribute_1.value.split(),
    )

    assert parser.test_attribute()
    for match in parser.parse():
        assert match.key == "huur"
        assert match.value == 1200.0

    parser = HuurParser(
        attribute=huur_attribute_2,
        tokens=huur_attribute_2.value.split(),
    )

    assert parser.test_attribute()
    for match in parser.parse():
        assert match.key == "huur"
        assert match.value == 2650.0


def test_waarborg_parser():
    waarborg_attribute = Attribute(key="Waarborgsom", value="€ 2.650")

    parser = WaarborgParser(
        attribute=waarborg_attribute,
        tokens=waarborg_attribute.value.split(),
    )

    assert parser.test_attribute()
    for match in parser.parse():
        assert match.key == "borg"
        assert match.value == 2650.0


def test_with_strange_values():
    """Test with strange values like: "value": "75 m\u00b2" """
    attribute = Attribute(key="Woonoppervlakte", value="75 m\u00b2")

    parser = OppervlakteParser(
        attribute=attribute,
        tokens=attribute.value.split(),
    )

    assert parser.test_attribute()
    for match in parser.parse():
        assert match.key == "oppervlakte"
        assert match.value == 75

    attribute_2 = Attribute(value="75m2")

    parser = OppervlakteParser(
        attribute=attribute_2,
        tokens=attribute_2.value.split(),
    )

    assert parser.test_attribute()
    for match in parser.parse():
        assert match.key == "oppervlakte"
        assert match.value == 75

    attribute_3 = Attribute(key="Woonoppervlakte", value="75 m2")

    parser = OppervlakteParser(
        attribute=attribute_3,
        tokens=attribute_3.value.split(),
    )

    assert parser.test_attribute()
    for match in parser.parse():
        assert match.key == "oppervlakte"
        assert match.value == 75


def test_parsing_test():
    """Test the parsing function."""

    attributes = [
        Attribute(key="Kamers", value="3 kamers"),
        Attribute(value="3 slaapkamers"),
        Attribute(key="Woonoppervlakte", value="75 m2"),
        Attribute(key="Perceel oppervlakte", value="155 m\u00b2"),
        Attribute(
            key="Huurprijs", value="€ 2.250.01 per maand (servicekosten onbekend)"
        ),
        Attribute(key="Waarborgsom", value="€2.650"),
        Attribute(key="Adres", value="Kerkstraat 1"),
        Attribute(key="Soort", value="Appartement"),
    ]

    parsers = [KamerParser, HuurParser, OppervlakteParser, WaarborgParser]

    parsed_attributes = parse_attributes(parsers=parsers, attributes=attributes)

    assert parsed_attributes["kamer"] == 3
    assert parsed_attributes["slaapkamer"] == 3
    assert parsed_attributes["oppervlakte"] == 75
    assert parsed_attributes["borg"] == 2650
    assert parsed_attributes["huur"] == 2250.01
