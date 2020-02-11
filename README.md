# sgit

Sub-git / Submodules-git


## Usage

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

To add a git repo that you want to track run

```
sgit repo add pykwalify git@github.com:Grokzen/pykwalify.git master

# To add a second project

sgit repo add redis git@github.com:Grokzen/redis-py-cluster.git master
```

To do the initial pull of the repos and move the repo to the specified revision run

```
sgit update pykwalify

sgit update redis
```

This will glone the git repos to your current cwd and update them to the master branch in our example above.

`sgit` relies on your own ssh config or other git config is properly setup and configured in sucha way that you can clone the git repo without having to specify any other credentials or similar inside the git repo.



## Update a repos revision

To move a repo to a new revision you do the following. Note that moving branches is only supported right now.

```
# This branch might not exist forever so update to some existing branch that you can find with "git branch -a" inside the git repo itself.

sgit repo set redis rev feature/multi-key-commands-in-pipelines
```

Update the git repo and move the `HEAD` to the new specified branch.

```
sgit update redis
```


## Development

Create a virtualenvrionment on your system.

Install all runtime dependencies, development dependencies and the package in local editable mode with `pip install -e ".[dev]"`

To run all unit tests run `pytest` from the root folder.
