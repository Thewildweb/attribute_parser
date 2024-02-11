from typing import Generator, Type
from collections.abc import Callable

from .attribute_parser import Attribute, Match, AttributeParser


def parse_attributes(
    parsers: list[AttributeParser],
    attributes: list[Attribute | dict[str, str]],
    tokenizer: Callable[[str], list[str]] = lambda x: x.split(),
) -> dict[str, float | int | str]:
    found_matches: list[Match] = []
    while True:
        if not attributes:
            break

        attribute = attributes.pop(0)

        if isinstance(attribute, dict):
            attribute = Attribute(attribute["value"], attribute.get("key"))

        attribute.tokens = tokenizer(attribute.value)

        for attr_parser in parsers:
            if not attr_parser.test_attribute(attribute):
                continue

            for item in attr_parser.parse(attribute):
                if isinstance(item, Attribute):
                    attributes.append(item)
                    continue

                found_matches.append(item)

    return_dict: dict[str, Match] = {}
    for match in found_matches:
        if not return_dict.get(match.key):
            return_dict[match.key] = match
            continue

        if match.merger:
            return_dict[match.key] = match.merger(return_dict[match.key], match)

    return {key: match.value for key, match in return_dict.items()}
