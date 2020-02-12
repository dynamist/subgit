# sgit

Sub-git / Submodules-git

The main purpose of this tool is to be used as a sync for cases where we need to pull together a set of different git repos into a single collection in one spot.

The main two advantages over other solutions is that when compared to the normal git submodules, you can more easily specify and avoid having to commit into your tree every single update that you want to have in your sgit checkout. In a submodule solution where you want to update and track the current and latest commit for the maste branch, you do not have to update your configuration file each time you make a new commit in the child repo. In the cases where you are pointing to tags and stable releases of a software, there is not much difference. When comparing to other tools that manipulates and pulls in each remote repos entire tree into your tree, this tool avoids that and dont care about that scenario. The only file you have to commit into a repo that you want sub repos to be exposed to is the `.sgit.yml` config file.

This tool has been primarly constructed to be a part inside a CI/CD solution where you want to in a build step, clone the repo that contains the `.sgit.yml` config file, clone out whatever branches or tags for all the child repos and then perform some action or build step or test or similar function while using all of the repos from one spot.


## Usage

### !!WARNING!!

Sgit do not leave any guarantees that it will not modify or throw away any local changes or modifications done to the git repo that it checks out and handles. Sgit is `NOT` in any way capable of commiting any changes or pushing any changes to your git remotes. This tool is only intended to be able to pull in and together a set of other git repos into one folder.


### Quickstart

Create a new folder where you want your sub repos to be located.

```
mkdir /tmp/sgit; cd /tmp/sgit
```

To initialize a brand new `.sgit.yml` config file run

```
sgit init

# To see the initial file content
cat .sgit.yml
```

Default config file content

```
repos: { }
```

To add a git repo that you want to track run

```
## Add first git repo
sgit repo add pykwalify git@github.com:Grokzen/pykwalify.git master

## Add second git repo
sgit repo add redis git@github.com:Grokzen/redis-py-cluster.git master
```

To do the initial pull/update of all repos in the config file and move the repo to the specified revision run

```
sgit update
```

Or you can update any specific repo you like by running

```
sgit update redis
```

This will glone the git repos to your current cwd and update them to the master branch in our example above.

`sgit` relies on your own ssh config or other git config is properly setup and configured in sucha way that you can clone the git repo without having to specify any other credentials or similar inside the git repo.


## List config file content and repo status

To view the content and all tracked git repos run

```
sgit list
```

Output

```
 ** All repos **

 - pykwalify
    URL: git@github.com:grokzen/pykwalify.git
    Tag: 1.7.0

 - redis
    URL: git@github.com:grokzen/redis-py-cluster.git
    Branch: master
```


## Update a repos revision

The command `sgit repo set` is used to manipulate existing repos in a config file.


### Update/set a branch revision

To move a repo to a new branch revision run

```
sgit repo set redis branch unstable

## Update the git repo and checkout the branch by running

sgit update redis
```

### Update/set a tag revision

To checkout a tag in a repo run

```
sgit repo set redis tag 1.0.0

## Update the git repo and checkout the tag by running

sgit update redis
```


## Development

Create a virtualenvrionment on your system.

Install all runtime dependencies, development dependencies and the package in local editable mode with

```
pip install -e ".[dev]"
```

To run all unit tests run `pytest` from the root folder.


## Project details

|   |   |
|---|---|
| python support         | 3.6, 3.7, 3.8 |
| Source                 | https://github.com/dynamist/sgit |
| Changelog              | https://github.com/dynamist/sgit/blob/master/CHANGELOG.md |
| Issues                 | https://github.com/dynamist/sgit/issues |
| pypi                   | https://pypi.python.org/pypi/sgit/ |
| License                | `Apache-2.0` https://github.com/dynamist/sgit/blob/master/LICENSE |
| Copyright              | `Copyright (c) 2019-2020 Dynamist AB` |
| git repo               | `git@github.com:dynamist/sgit.git` |
| install stable         | `pip install sgit` |
| required dependencies  | `docopt>=0.6.2`<br> `ruamel.yaml>=0.16.0`<br> `gitpython>=3.0.5` |
