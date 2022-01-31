# -*- coding: utf-8 -*-

# python std lib
import os
from datetime import datetime, timedelta

# sgit imports
from sgit.core import Sgit
from sgit.constants import *
from sgit.enums import *
from sgit.exceptions import *

# 3rd party imports
import pytest
from git import Git, Repo
from ruamel import yaml
from packaging.version import InvalidVersion


def test_filter(sgit):
    assert sgit._filter([], []) == []
    assert sgit._filter(["1.0.0"], []) == ["1.0.0"]

    with pytest.raises(SgitConfigException):
        sgit._filter(["1.0.0"], [""]) == []

    # Test basic failure cases where invalid and wrong values is passed into the method
    with pytest.raises(SgitConfigException):
        sgit._filter(None, None)

    with pytest.raises(SgitConfigException):
        sgit._filter([], None)

    # Wrong values passed into the regex module will cause exceptions
    with pytest.raises(SgitConfigException):
        sgit._filter([1], [1])

    assert sgit._filter(["1.0.0"], [r"(1.0)"]) == ["1.0"]
    assert sgit._filter(["1.0.0"], [r"(1.1)"]) == []

    # With a groupe that is not in the correct place we should not get out anything
    assert sgit._filter(["v1.0.0"], [r"([0-9].[0-9].[0-9])"]) == []

    # Only the value within the group will remain
    assert sgit._filter(["v1.0.0"], [r"v([0-9].[0-9].[0-9])"]) == ["1.0.0"]

    # Test valid cleaning with multiple values
    assert sgit._filter(["v1.0.0", "v2.0.0"], [r"v([0-9].[0-9].[0-9])"]) == ["1.0.0", "2.0.0"]

    # Test two different regex that both filters out the valid values and that extracts out
    # the version string we want to have
    assert sgit._filter(
        ["v1.0.0", "1a.b.c"],
        [
            r"[a-z]([0-9].[0-9].[0-9])",
            r"[0-9]([a-z].[a-z].[a-z])",
        ],
    ) == ["1.0.0", "a.b.c"]


def test_order_time(sgit):
    """
    Ordering by time assumes that we send in the following datastructure into the _order()

    It might be possible to sort on other keys other then datetime object, but when selecting TIME
    as an option it is assumed that the object should be datetime objects and the result will be reversed before returning

    [(str, datetime_obj), ...]
    """
    assert sgit._order(
        [],
        OrderAlgorithms.TIME,
    ) == []

    # We are not able to sort on TIME when items within do not contain any data
    with pytest.raises(IndexError):
        sgit._order(
            [()],
            OrderAlgorithms.TIME,
        )

    # Ensure always correct time ordering with offset times
    c = datetime.now() + timedelta(seconds=1)
    a = datetime.now() + timedelta(seconds=2)
    b = datetime.now() + timedelta(seconds=3)

    # Item with datetime b will be after item with datetime a as b was created after a
    # This will simulate that the latest tag will be put first in the list
    assert sgit._order(
        [("1.0.0", a), ("2.0.0", b), ("1.5.0", c)],
        OrderAlgorithms.TIME,
    ) == [("1.5.0", c), ("1.0.0", a), ("2.0.0", b)]

    assert sgit._order(
        [("2.0.0", b), ("1.0.0", a), ("1.5.0", c)],
        OrderAlgorithms.TIME,
    ) == [("1.5.0", c), ("1.0.0", a), ("2.0.0", b)]


def test_order_semver(sgit):
    assert sgit._order([], OrderAlgorithms.SEMVER) == []

    # Invalid semver versions should raise exception
    with pytest.raises(InvalidVersion):
        sgit._order(["a"], OrderAlgorithms.SEMVER)

    # When sorting by semver, the latest version should be the first item in the list.
    # By default the semver odering will put the latest version last in the list
    assert sgit._order(
        ["0.9.0", "1.0.0", "1.1.0"],
        OrderAlgorithms.SEMVER,
    ) == ["0.9.0", "1.0.0", "1.1.0"]


def test_order_alphabetical(sgit):
    assert sgit._order(["c", "a", "b"], OrderAlgorithms.ALPHABETICAL) == ["a", "b", "c"]
    
    assert sgit._order(["3", "1", "2"], OrderAlgorithms.ALPHABETICAL) == ["1", "2", "3"]


def test_select_semver(sgit):
    # Test that basic cases of PEP440 semver checks works as expected when we select that method
    assert sgit._select(
        ["1.1.0", "1.0.0", "0.9.0"],
        ">=1.0.0",
        SelectionMethods.SEMVER,
    ) == "1.0.0"

    assert sgit._select(
        ["1.1.0", "1.0.0", "0.9.0"],
        "<1.0.0",
        SelectionMethods.SEMVER,
    ) == "0.9.0"

    # Test reserved keywords "first" and "last"
    assert sgit._select(
        ["1.0.0", "0.9.0"],
        "last",
        SelectionMethods.SEMVER,
    ) == "0.9.0"

    assert sgit._select(
        ["0.9.0", "1.0.0"],
        "last",
        SelectionMethods.SEMVER,
    ) == "1.0.0"

    assert sgit._select(
        ["1.0.0", "0.9.0"],
        "first",
        SelectionMethods.SEMVER,
    ) == "1.0.0"

    assert sgit._select(
        ["0.9.0", "1.0.0"],
        "first",
        SelectionMethods.SEMVER,
    ) == "0.9.0"


def test_select_exact(sgit):
    # Given we want one and one exact value from our list of objects
    assert sgit._select(
        ["1.1.0", "1.0.0", "0.9.0"],
        "1.0.0",
        SelectionMethods.EXACT,
    ) == "1.0.0"

    # If we provide a value to select that do not exists we should get None back out
    assert sgit._select(
        ["1.1.0", "1.0.0", "0.9.0"],
        "0.0.0",
        SelectionMethods.EXACT,
    ) == None


def test_select_failure(sgit):
    # If we provide a enum value that do not exists and is invalid we should get exception
    with pytest.raises(SgitConfigException):
        sgit._select([], "", 123456789)


def test_chain(sgit):
    """
    This test would match the following working .sgit.yml configuration file

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
    import random
    input_sequence = ["1.0.0", "15.10", "18.10", "v0.9.0", "1.8.0"]
    random.shuffle(input_sequence)

    print(f" -- Input sequence {input_sequence}")

    filter_output = sgit._filter(input_sequence, ["[0-9].[0-9].[0-9]"])
    print(f" -- Filter output {filter_output}")

    order_output = sgit._order(filter_output, OrderAlgorithms.SEMVER)
    print(f" -- Order output {order_output}")

    select_output = sgit._select(order_output, "last", SelectionMethods.SEMVER)
    print(f" -- Select last output {select_output}")
    assert select_output == "1.8.0"

    select_output = sgit._select(order_output, ">=0.7.0", SelectionMethods.SEMVER)
    print(f" -- Select >=0.7.0 output {select_output}")
    assert select_output == "1.8.0"

    select_output = sgit._select(order_output, "<1.5.0", SelectionMethods.SEMVER)
    print(f" -- Select <1.0.0 output {select_output}")
    assert select_output == "1.0.0"
