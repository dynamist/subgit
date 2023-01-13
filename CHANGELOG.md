# 0.6.0

## Prelude

Added new features and commands, such as:

- 'subgit delete'
- 'subgit import'
- 'subgit reset'
- 'subgit clean'

## General fixes

- Added error handling for 'subgit pull'.
	- If subgit config file has a repo with `branch: `, the command exits

- Implemented multiprocessing for 'subgit fetch' commnand. [#41][https://github.com/dynamist/subgit/pull/41]

## New features

* [#42][https://github.com/dynamist/subgit/pull/42] - Added function to render all repos from a github/gitlab user account/organisation
* [#41][https://github.com/dynamist/subgit/pull/41] - Implemented multiprocessing to 'subgit fetch' command
* [#37][https://github.com/dynamist/subgit/pull/37] - Added '--conf' flag to use optional file name for subgit config
* [#36][https://github.com/dynamist/subgit/pull/36] - Added 'subgit delete' command

## Other notes

* [#38][https://github.com/dynamist/subgit/pull/38] - Added a mailmap to repo

# 0.5.0
