# 0.6.2 (2023-03-29)

## Fixes

- Fixed bug in 'subgit init' where the command would not work if there was no '.subgit.yml' file present. [#51](https://github.com/dynamist/subgit/pull/51)
- Fixed bug in 'subgit pull' where subgit would not do a pull if there are changes on the remote. [#52](https://github.com/dynamist/subgit/pull/52)
- Renamed sub-command 'subgit import' to 'subgit inspect'. This command will no longer write a new subgit config file. Instead it will write the configuration file to stdout as it would look so the user can redirect the output in to a file of their choice. [#53](https://github.com/dynamist/subgit/pull/53)

# 0.6.1 (2023-02-02)

## Fixes

- Add missing python package `subgit.importer` to built wheels and sdist packages


# 0.6.0 (2023-01-13)

## Prelude

With this release our intentions were to expand this tool with features that makes the everyday use more efficient. Some new features are made to emulate the existing 'git' commands, while others are specific for the 'subgit' tool. Maybe most useful in some CI/CD practices. 

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
