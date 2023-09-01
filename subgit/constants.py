# -*- coding: utf-8 -*-

DEFAULT_REPO_DICT = {
    "repos": [
        {
            "name": "subgit",
            "url": "git@github.com:dynamist/subgit.git",
            "revision": {
                "branch": "master",
            },
        }
    ]
}

REVISION_BRANCH = "branch"
REVISION_COMMIT = "commit"
REVISION_TAG = "tag"

WORKER_COUNT = 8

__all__ = [
    "DEFAULT_REPO_DICT",
    "REVISION_BRANCH",
    "REVISION_COMMIT",
    "REVISION_TAG",
    "WORKER_COUNT",
]
