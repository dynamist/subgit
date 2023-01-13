# 0.6.0

## Prelude

Added new features and commands:

- 'subgit delete'
- 'subgit import'
- 'subgit reset'
- 'subgit clean'

## Fixes

- Added additional error handling for 'subgit pull' that checks if subgit config file has a repo with empty branch: `branch: `. If so, command fails.

- Implemented multiprocessing for 'subgit fetch' commnand. [#41](https://github.com/dynamist/subgit/pull/41)

- Added mailmap to repo. [#38](https://github.com/dynamist/subgit/pull/38)

## New features

* [#42](https://github.com/dynamist/subgit/pull/42) - Added function to write all repos from a github/gitlab user account/organisation to config file
* [#37](https://github.com/dynamist/subgit/pull/37) - Added '--conf' flag to use optional file name for subgit config
* [#36](https://github.com/dynamist/subgit/pull/36) - Added 'subgit delete' command

# 0.5.0
