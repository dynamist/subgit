# sgit

The name came originally from "Submodules Git", or more commonly "Sub Git".

The main purpose of this tool is to be used as a sync for cases to pull together a set of different Git repos into a deterministic directory tree. It is used to collect various individual parts into a whole.

The main two advantages over other solutions is that when compared to the normal git submodules, you can more easily specify and avoid having to commit into your tree every single update that you want to have in your sgit checkout. In a submodule solution where you want to update and track the current and latest commit for the maste branch, you do not have to update your configuration file each time you make a new commit in the child repo. In the cases where you are pointing to tags and stable releases of a software, there is not much difference. When comparing to other tools that manipulates and pulls in each remote repos entire tree into your tree, this tool avoids that and dont care about that scenario. The only file you have to commit into a repo that you want sub repos to be exposed to is the `.sgit.yml` config file.

This tool has been primarly constructed to be a part inside a CI/CD solution where you want to in a build step, clone the repo that contains the `.sgit.yml` config file, clone out whatever branches or tags for all the child repos and then perform some action or build step or test or similar function while using all of the repos from one spot.


## Usage

### !!WARNING!!

Sgit do not leave any guarantees that it will not modify or throw away any local changes or modifications done to the git repo that it checks out and handles. Sgit is `NOT` in any way capable of commiting any changes or pushing any changes to your git remotes. This tool is only intended to be able to pull in and together a set of other git repos into one folder.


### Quickstart

Create a new folder where you want your sub repos to be located

```
mkdir /tmp/sgit; cd /tmp/sgit
```

Initialize an empty `.sgit.yml` config file

```
sgit init
```

Inspect the content by looking inside the `.sgit.yml` config file

```
cat .sgit.yml
```

Default content of the configuration file for a new initialized repo

```
repos: { }
```

To add any number of git repos that you want to clone

```
sgit repo add pykwalify git@github.com:Grokzen/pykwalify.git
```

You can optionally specify the target branch you want to clone by adding it at after the clone url

```
sgit repo add redis git@github.com:Grokzen/redis-py-cluster.git master
```

Then proceed to the initial clone/pull of all repos in the config file and move the repo to the specified revision

```
sgit update
```

Or you can update a specific repo

```
sgit update redis
```

sgit relies on your own ssh config or other git config is properly setup and configured in sucha way that you can clone the git repo without having to specify any other credentials or similar inside the git repo.


## List config file content and repo status

View the content and all tracked git repos

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

To move a repo to a new branch revision

```
sgit repo set redis branch unstable
```

Update the git repo and checkout the branch

```
sgit update redis
```

### Update/set a tag revision

To checkout a tag in a repo

```
sgit repo set redis tag 1.0.0
```

Update the git repo and checkout the tag

```
sgit update redis
```

## Development

Create a virtualenv (venv) on your system

Install all runtime dependencies, development dependencies and the package in local editable mode

```
pip install -e ".[dev]"
```

To run all unit tests run `pytest` from the root folder


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
