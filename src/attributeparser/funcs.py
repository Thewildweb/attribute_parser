"""Some helper functions"""
import re
from collections.abc import Iterator


def terms_in_tokens(
    tokens: list[str],
    terms: str | re.Pattern | list[str | re.Pattern],
    index: int,
    distance: int = 1,
    before: bool = True,
    after: bool = True,
) -> bool:
    """Test if one or multiple terms are in the tokens.
    Terms can be a single string, a regex pattern or a list of strings or regex patterns
    """
    if not isinstance(terms, list):
        terms = [terms]

    for token in get_tokens_near_index(
        tokens, index, distance=distance, before=before, after=after
    ):
        for term in terms:
            if isinstance(term, str):
                if term in token:
                    return True
                continue
            if term.match(token):
                return True

    return False


def get_tokens_near_index(
    tokens, index: int, distance: int = 1, before: bool = True, after: bool = True
) -> Iterator[str]:
    """Get tokens near index"""
    # get the section before the index and reverse it
    tokens_before_index = tokens[:index]
    tokens_after_index = tokens[index + 1 :]

    for _ in range(distance):
        if before and tokens_before_index:
            yield tokens_before_index.pop()

        if after and tokens_after_index:
            yield tokens_after_index.pop(0)

        if not tokens_before_index and not tokens_after_index:
            break


def terms_in_text(
    text: str,
    terms: str | re.Pattern | list[str | re.Pattern],
) -> bool:
    """Test is one or multiple terms are in the key.
    Terms can be a single string, a regex pattern or a list of strings or regex patterns
    """
    if not isinstance(terms, list):
        terms = [terms]

    for term in terms:
        if isinstance(term, str):
            if term in text:
                return True
            continue
        if term.match(text):
            return True

    return False


def money_repr(word: str) -> float | None:
    """Takes a string and tries to return a float that represents money, that
    could have two decimals. If it fails, it returns None.
    >>> money_repr("1.000,00")
    1000.0
    >>> money_repr("10")
    10.0
    >>> money_repr("1.000.00")
    100000.0
    """
    decimal = None
    if len(word) > 3:
        if word[-3] == "." or word[-3] == ",":
            decimal = word[-2:]
            word = word[:-3]

    word = word.replace(".", "").replace(",", "")
    if word.isdigit():
        if decimal:
            word = word + "." + decimal
        return float(word)
    return None
