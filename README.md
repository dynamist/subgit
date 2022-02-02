# sgit

The name came originally from "Submodules Git", or more commonly "Sub Git".

The main purpose of this tool is to be used as a sync for cases to pull together a set of different Git repos into a deterministic directory tree. It is used to collect various individual parts into a whole.

The main two advantages over other solutions is that when compared to the normal git submodules, you can more easily specify and avoid having to commit into your tree every single update that you want to have in your sgit checkout. In a submodule solution where you want to update and track the current and latest commit for the maste branch, you do not have to update your configuration file each time you make a new commit in the child repo. In the cases where you are pointing to tags and stable releases of a software, there is not much difference. When comparing to other tools that manipulates and pulls in each remote repos entire tree into your tree, this tool avoids that and dont care about that scenario. The only file you have to commit into a repo that you want sub repos to be exposed to is the `.sgit.yml` config file.

This tool has been primarly constructed to be a part inside a CI/CD solution where you want to in a build step, clone the repo that contains the `.sgit.yml` config file, clone out whatever branches or tags for all the child repos and then perform some action or build step or test or similar function while using all of the repos from one spot.


## Usage

### !!WARNING!!

Sgit do not leave any guarantees that it will NOT MODIFY or THROW AWAY any local changes or modifications done to the git repo that it checks out and handles. Sgit is `NOT` in any way capable of commiting any changes or pushing any changes to your git remotes. This tool is only intended to be able to pull in and together a set of other git repos into one folder.

In addition to `sgit`, you will also get an `git-sub` command, that when used as `git sub [...]` will be invoked properly. A neat way to expose this tool in a way that integrates with your Git workflow.

### Quickstart

Install the tool with `pip install py-sgit`. The tool requires python version >= 3.8.0

Create a temporary folder where you want your sub repos to be located

```bash
mkdir /tmp/sgit; cd /tmp/sgit
```

Initialize an empty `.sgit.yml` config file

```bash
sgit init
```

Inspect the content by looking inside the `.sgit.yml` config file

```bash
cat .sgit.yml

# This will show the default config in an empty config file

repos: { }
```

To add any number of git repos that you want to clone.

You can optionally specify the target branch you want to clone by adding it at after the clone url. It will default to `master` branch as most git repos still use that. If you are using `main` as your default branch you need to specify that explicitly.

```bash
sgit repo add pykwalify git@github.com:Grokzen/pykwalify.git master
```

Next step is to make the initial git clone/pull of all repos in the config file and move the repo to the specified revision. Running `sgit update` command without any arguments will update all repos defined in the configuration file. If your repo is not present on disk it will make a inidial `git clone` before moving to your selected revision.

```bash
sgit update
```

Or you can update a specific repo from your config file.

```bash
sgit update pykwalify
```

Sgit relies on your own ssh config or other git config is properly setup and configured in sucha way that you can clone the git repo without having to specify any other credentials or similar inside the git repo.

You can view a summary of your current repo and config state by running

```bash
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

To move a repo to a new branch if you want for example to switch from `master` to `develop`.

```bash
sgit repo set pykwalify branch develop
```

Update the git repo and checkout the branch

```bash
sgit update pykwalify
```

There is much more extensive docuemtnation and examples for this feature in `docs/revision-branch.md`.


### Update/set a tag revision

To checkout a tag in a repo.

```bash
sgit repo set pykwalify tag 1.0.0
```

Update the git repo and checkout the tag

```bash
sgit update pykwalify
```

There is much more extensive documentation and examples for this feature in `docs/revision-tag.md`


## Fetch changes in a repo

If you want to `git fetch` all or a subset of git repos in your config then you can use the `sgit fetch` command. The benefit of doing a fetch is that you can fetch home all changes to a set of git repos but you do not have to update and move each repo to a new commit. In general git operations, it is always more safe to run `git fetch` before you do a checkout or `git pull` to update your local cloned repos. This allows you to inspect the changes incomming before commiting to pulling them.

Sgit fetch command supports the selection of either all repos or a subset of repos. The fetch command will never prompt the user asking if they want to do a update as fetch is considered a non-descrutive command.

```bash
# Fetch all repos in sequence
sgit fetch

# Fetch one specific repo
sgit fetch pykwalify
```


## Development

Create a virtualenv (venv) on your system.

Install all runtime dependencies, test dependencies, development dependencies and the package in local editable mode with

```bash
pip install -e ".[dev,test]"
```

To run all unit tests run `pytest` from the root folder.


### Extra development option flags

You can currently use the following envroinment flags `DEBUG=1` to get additional debugging and detailed information about any uncaught exceptions and detailed information about cli flags etc.

To get into a PDB debugger on any uncaught exceptions you can set the environment flag `PDB=1` and that will take you into a pdb debugger at the cli exit point so you can dig into any issues you might have.


## Python support guidelines

We follow the method of always suporting the latest released major version of python and two major versions back. This gives us backwards compatibility for about 2-3 years depending on the release speed of new python versions.

When a new major version is incorporated, tested and validated it works as expected and that dependencies is not broken, the update for new python version support should be released with the next major version of sgit. A major python version should never be dropped in a minor version update.

Python 2.7 is EOL and that version will not be supported at all moving forward.


## Project details

|   |   |
|---|---|
| python support         | 3.8, 3.9, 3.10 |
| Source code            | https://github.com/dynamist/sgit |
| Changelog              | https://github.com/dynamist/sgit/blob/master/CHANGELOG.md |
| Issues                 | https://github.com/dynamist/sgit/issues |
| Projects page          | https://github.com/dynamist/sgit/projects/1
| pypi                   | https://pypi.python.org/pypi/sgit/ |
| License                | `Apache-2.0` https://github.com/dynamist/sgit/blob/master/LICENSE |
| Copyright              | `Copyright (c) 2019-2021 Dynamist AB` |
| git repo               | `git@github.com:dynamist/sgit.git` |
| install stable         | `pip install py-sgit` |
