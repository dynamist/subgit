# -*- coding: utf-8 -*-

# python std lib
import random
from datetime import datetime, timedelta

# subgit imports
from subgit.constants import *
from subgit.enums import *
from subgit.exceptions import *

# 3rd party imports
import pytest
from packaging.version import InvalidVersion


def test_filter(subgit):
    assert subgit._filter([], []) == []
    assert subgit._filter(["1.0.0"], []) == ["1.0.0"]

    with pytest.raises(SubGitConfigException):
        subgit._filter(["1.0.0"], [""]) == []

    # Test basic failure cases where invalid and wrong values is passed into the method
    with pytest.raises(SubGitConfigException):
        subgit._filter(None, None)

    with pytest.raises(SubGitConfigException):
        subgit._filter([], None)

    # Wrong values passed into the regex module will cause exceptions
    with pytest.raises(SubGitConfigException):
        subgit._filter([1], [1])

    assert subgit._filter(["1.0.0"], [r"(1.0)"]) == ["1.0"]
    assert subgit._filter(["1.0.0"], [r"(1.1)"]) == []

    # With a groupe that is not in the correct place we should not get out anything
    assert subgit._filter(["v1.0.0"], [r"([0-9].[0-9].[0-9])"]) == []

    # Only the value within the group will remain
    assert subgit._filter(["v1.0.0"], [r"v([0-9].[0-9].[0-9])"]) == ["1.0.0"]

    # Test valid cleaning with multiple values
    assert subgit._filter(["v1.0.0", "v2.0.0"], [r"v([0-9].[0-9].[0-9])"]) == ["1.0.0", "2.0.0"]

    # Test two different regex that both filters out the valid values and that extracts out
    # the version string we want to have
    assert subgit._filter(
        ["v1.0.0", "1a.b.c"],
        [
            r"[a-z]([0-9].[0-9].[0-9])",
            r"[0-9]([a-z].[a-z].[a-z])",
        ],
    ) == ["1.0.0", "a.b.c"]


def test_order_time(subgit):
    """
    Ordering by time assumes that we send in the following datastructure into the _order()

    It might be possible to sort on other keys other then datetime object, but when selecting TIME
    as an option it is assumed that the object should be datetime objects and the result will be reversed before returning

    [(str, datetime_obj), ...]
    """
    assert subgit._order(
        [],
        OrderAlgorithms.TIME,
    ) == []

    # We are not able to sort on TIME when items within do not contain any data
    with pytest.raises(IndexError):
        subgit._order(
            [()],
            OrderAlgorithms.TIME,
        )

    # Ensure always correct time ordering with offset times
    c = datetime.now() + timedelta(seconds=1)
    a = datetime.now() + timedelta(seconds=2)
    b = datetime.now() + timedelta(seconds=3)

    # Item with datetime b will be after item with datetime a as b was created after a
    # This will simulate that the latest tag will be put first in the list
    assert subgit._order(
        [("1.0.0", a), ("2.0.0", b), ("1.5.0", c)],
        OrderAlgorithms.TIME,
    ) == [("1.5.0", c), ("1.0.0", a), ("2.0.0", b)]

    assert subgit._order(
        [("2.0.0", b), ("1.0.0", a), ("1.5.0", c)],
        OrderAlgorithms.TIME,
    ) == [("1.5.0", c), ("1.0.0", a), ("2.0.0", b)]


def test_order_semver(subgit):
    assert subgit._order([], OrderAlgorithms.SEMVER) == []

    # Invalid semver versions should raise exception
    with pytest.raises(InvalidVersion):
        subgit._order(["a"], OrderAlgorithms.SEMVER)

    # When sorting by semver, the latest version should be the first item in the list.
    # By default the semver odering will put the latest version last in the list
    assert subgit._order(
        ["0.9.0", "1.0.0", "1.1.0"],
        OrderAlgorithms.SEMVER,
    ) == ["0.9.0", "1.0.0", "1.1.0"]


def test_order_alphabetical(subgit):
    assert subgit._order(["c", "a", "b"], OrderAlgorithms.ALPHABETICAL) == ["a", "b", "c"]

    assert subgit._order(["3", "1", "2"], OrderAlgorithms.ALPHABETICAL) == ["1", "2", "3"]


def test_select_semver(subgit):
    # Test that basic cases of PEP440 semver checks works as expected when we select that method
    assert subgit._select(
        ["1.1.0", "1.0.0", "0.9.0"],
        ">=1.0.0",
        SelectionMethods.SEMVER,
    ) == "1.0.0"

    assert subgit._select(
        ["1.1.0", "1.0.0", "0.9.0"],
        "<1.0.0",
        SelectionMethods.SEMVER,
    ) == "0.9.0"

    # Test reserved keywords "first" and "last"
    assert subgit._select(
        ["1.0.0", "0.9.0"],
        "last",
        SelectionMethods.SEMVER,
    ) == "0.9.0"

    assert subgit._select(
        ["0.9.0", "1.0.0"],
        "last",
        SelectionMethods.SEMVER,
    ) == "1.0.0"

    assert subgit._select(
        ["1.0.0", "0.9.0"],
        "first",
        SelectionMethods.SEMVER,
    ) == "1.0.0"

    assert subgit._select(
        ["0.9.0", "1.0.0"],
        "first",
        SelectionMethods.SEMVER,
    ) == "0.9.0"


def test_select_exact(subgit):
    # Given we want one and one exact value from our list of objects
    assert subgit._select(
        ["1.1.0", "1.0.0", "0.9.0"],
        "1.0.0",
        SelectionMethods.EXACT,
    ) == "1.0.0"

    # If we provide a value to select that do not exists we should get None back out
    assert subgit._select(
        ["1.1.0", "1.0.0", "0.9.0"],
        "0.0.0",
        SelectionMethods.EXACT,
    ) is None


def test_select_failure(subgit):
    # If we provide a enum value that do not exists and is invalid we should get exception
    with pytest.raises(SubGitConfigException):
        subgit._select([], "", 123456789)


def test_chain(subgit):
    """
    This test would match the following working .subgit.yml configuration file

    repos:
      pykwalify:
        url: foo
        revision:
          tag:
            filter:"[0-9].[0-9].[0-9]"
            order: semver
            select: >=1.8.0

    and if the tags from this git repo still works as expected you should get out the latest
    git tag from the repo based on semver logic which would be 1.8.0
    """
    input_sequence = ["1.0.0", "15.10", "18.10", "v0.9.0", "1.8.0"]
    random.shuffle(input_sequence)

    print(f" -- Input sequence {input_sequence}")

    filter_output = subgit._filter(input_sequence, ["[0-9].[0-9].[0-9]"])
    print(f" -- Filter output {filter_output}")

    order_output = subgit._order(filter_output, OrderAlgorithms.SEMVER)
    print(f" -- Order output {order_output}")

    select_output = subgit._select(order_output, "last", SelectionMethods.SEMVER)
    print(f" -- Select last output {select_output}")
    assert select_output == "1.8.0"

    select_output = subgit._select(order_output, ">=0.7.0", SelectionMethods.SEMVER)
    print(f" -- Select >=0.7.0 output {select_output}")
    assert select_output == "1.8.0"

    select_output = subgit._select(order_output, "<1.5.0", SelectionMethods.SEMVER)
    print(f" -- Select <1.0.0 output {select_output}")
    assert select_output == "1.0.0"
