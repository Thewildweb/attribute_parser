from typing import Any
from collections.abc import Iterator, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import html


@dataclass
class Attribute:
    """The Attribute class represents the attribute of the object."""

    def __init__(
        self,
        value: str,
        key: str | None = None,
        html: str | None = None,
        tokens: list[str] | None = None,
    ) -> None:
        self.value = value
        self.key = key
        self.html = html
        self.tokens = tokens


class Match:
    """The Match class represents a match found in the AttributeParser."""

    def __init__(
        self,
        value: int | float | str,
        key: str,
        attribute: Attribute,
        merger: Callable[["Match", "Match"], "Match"] | None = None,
    ) -> None:
        self.value = value
        self.key = key
        self.attribute = attribute
        self.merger = merger

    def __repr__(self) -> str:
        return f"<Match {self.key}={self.value}>"

    def __str__(self) -> str:
        return self.__repr__()

    def merge(self, other: "Match") -> "Match" | None:
        """When two matches with the same keyword are found, this method
        decides what to do with them. By default it replaces the old match
        with the new one.
        """
        if self.key != other.key:
            return None

        if self.merger:
            return self.merger(self, other)
        return other


class AttributeParser(ABC):
    """Parse an attribute"""

    name: str = "AttributeParser"

    def __init__(
        self,
        attribute: Attribute,
    ) -> None:
        self.value = html.unescape(attribute.value)
        self.key = html.unescape(attribute.key) if attribute.key else None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    def create_match(
        self,
        value: Any,
        key: str,
        merger: Callable[[Match, Match], Match] | None = None,
    ) -> Match:
        """Create a match"""
        return Match(
            value=value,
            key=key,
            attribute=Attribute(value=self.value, key=self.key),
            merger=merger,
        )

    @abstractmethod
    def test_attribute(self, attribute: Attribute) -> bool:
        """Test if the attribute can be parsed by this parsed"""
        raise NotImplemented

    @abstractmethod
    def parse(self, attribute: Attribute) -> Iterator[Match]:
        """Parse the Attribute. This method should yield a Match or an Attribute
        that needs further matching."""
        raise NotImplemented
