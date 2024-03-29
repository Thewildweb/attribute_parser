import re
import os
import sys
from collections.abc import Iterator

from nltk.tokenize import word_tokenize  # type: ignore

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.attributeparser.attribute_parser import AttributeParser, Match, Attribute
from src.attributeparser.funcs import money_repr, terms_in_tokens, terms_in_text


def return_highest(self, other):
    """When two matches with the same keyword are found, this method
    decides what to do with them. By default it replaces the old match
    with the new one.
    """
    if self.value < other.value:
        return other
    return self


class KamerParser(AttributeParser):
    name = "Kamer Parser"

    def test_key_value(self, attribute) -> bool:
        """Test both the value and the key"""

        if "kamer" in attribute.value.lower():
            return True
        if attribute.key and "kamer" in attribute.key.lower():
            return True
        return False

    def test_attribute(self, attribute) -> bool:
        """Test if the attribute can be parsed by this parser"""

        return self.test_key_value(attribute)

    def value_parser(self, value: str, *args, **kwargs) -> int:
        """Parse the value"""

        return int(value)

    def parse(self, attribute) -> Iterator[Match]:
        """Parse the value"""
        tokens = attribute.tokens
        if not tokens:
            tokens = attribute.value.split()

        for count, token in enumerate(tokens):
            if token.isdigit():
                pattern_list: list[tuple[str, re.Pattern]] = [
                    ("slaapkamer", re.compile(r"slaap", re.IGNORECASE)),
                    ("badkamer", re.compile(r"bad", re.IGNORECASE)),
                    ("wc", re.compile(r"(wc|toilet)", re.IGNORECASE)),
                    ("kamer", re.compile(r"kamer", re.IGNORECASE)),
                ]

                for key, pattern in pattern_list:
                    if terms_in_tokens(
                        tokens=tokens,
                        terms=pattern,
                        index=count,
                        distance=1,
                        before=False,
                    ) or (
                        attribute.key
                        and terms_in_text(text=attribute.key, terms=pattern)
                    ):
                        yield self.create_match(
                            value=int(token),
                            key=key,
                            attribute=attribute,
                            merger=return_highest,
                        )
                        continue


class HuurParser(AttributeParser):
    name = "Huur Parser"
    terms = [
        "huur",
        "prijs",
    ]
    match_key = "huur"

    def test_key_value(self, attribute: Attribute) -> bool:
        """Test both the value and the key"""

        for term in self.terms:
            if term in attribute.value.lower():
                return True

            if attribute.key and term in attribute.key.lower():
                return True

        return False

    def test_attribute(self, attribute: Attribute) -> bool:
        """Test if the attribute can be parsed by this parser"""

        return self.test_key_value(attribute)

    @staticmethod
    def tokenizer(value: str) -> list[str]:
        """Tokenize the value"""
        # if a € is attached to a digit add a space in between
        clean_value = re.sub(r"€(\d)", r"€ \1", value)
        return word_tokenize(clean_value)

    def parse(self, attribute: Attribute) -> Iterator[Match]:
        """Parse the value"""
        tokens = self.tokenizer(attribute.value)

        for token in tokens:
            if amount := money_repr(token):
                yield self.create_match(
                    value=amount, key=self.match_key, attribute=attribute
                )


class WaarborgParser(HuurParser):
    name = "Waarborg Parser"
    terms = [
        "borg",
    ]
    match_key = "borg"


def merge_oppervlakte(one, other):
    """When two matches with the same keyword are found, this method
    decides what to do with them. By default it replaces the old match
    with the new one.
    """
    keywords = [
        "oppervlakte",
        "wonen",
        "woon",
    ]
    one_list = []
    if one.attribute.key:
        one_list = [k in one.attribute.key.lower() for k in keywords]
    other_list = []
    if other.attribute.key:
        other_list = [k in other.attribute.key.lower() for k in keywords]

    if one_list > other_list:
        return one
    elif one_list < other_list:
        return other

    if one.value < other.value:
        return other
    return one


class OppervlakteParser(AttributeParser):
    name = "Oppervlakte Parser"

    @staticmethod
    def test_key(key: str) -> bool:
        """Test the key"""

        terms = [
            "oppervlakte",
            "wonen",
            "woon",
            "leef",
        ]
        if key:
            if not any([t in key.lower() for t in terms]):
                return False

        return True

    @staticmethod
    def test_value(value: str) -> bool:
        """Test the value"""

        terms = [
            "m2",
            "m²",
        ]
        if not any([t in value.lower() for t in terms]):
            return False

        return True

    def test_attribute(self, attribute: Attribute) -> bool:
        """Test if the attribute can be parsed by this parser"""

        if attribute.key and self.test_key(attribute.key):
            return True
        return self.test_value(attribute.value)

    @staticmethod
    def tokenizer(text: str) -> list[str]:
        """Tokenize the value"""
        text = text.replace("\u00b2", "2")
        tokens = word_tokenize(text)

        items: list[tuple[tuple[str, str], int]] = []
        for token in tokens:
            # test if token is a number with a square meter sign
            # or m2 or m², and split this token up and not the index of
            # the token
            if token[-2:] == "m²" or token[-2:] == "m2":
                items.append(((token[:-2], token[-2:]), tokens.index(token)))

        for item, index in items:
            tokens[index] = item[0]
            tokens.insert(index + 1, item[1])

        return tokens

    def parse(self, attribute: Attribute) -> Iterator[Match]:
        """Parse the value"""
        tokens = self.tokenizer(attribute.value)

        for count, token in enumerate(tokens):
            if token.isdigit():
                if terms_in_tokens(
                    tokens=tokens,
                    terms=["m2", "m²"],
                    index=count,
                    distance=2,
                    before=False,
                ):
                    yield self.create_match(
                        value=int(token),
                        key="oppervlakte",
                        attribute=attribute,
                        merger=merge_oppervlakte,
                    )
                    continue
