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

Default config file content

```
repos: { }
```

To add a git repo that you want to track run

```
## Add first git repo
sgit repo add pykwalify git@github.com:grokzen/pykwalify.git master

## Add second git repo
sgit repo add redis git@github.com:grokzen/redis-py-cluster.git master
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

To view the content and all tracked git repos run

```
sgit repo list
```

Output

```
 ** All repos **

 - pykwalify
   - URL: git@github.com:grokzen/pykwalify.git
   - Rev: master

 - redis
   - URL: git@github.com:grokzen/redis-py-cluster.git
   - Rev: master
```


## Update a repos revision

To move a repo to a new revision you do the following. Note that moving branches is only supported right now.

```
## This branch might not exist forever so update to some existing branch that
## you can find with "git branch -a" inside the git repo itself.

sgit repo set redis rev feature/multi-key-commands-in-pipelines
```

Update the git repo and move the `HEAD` to the new specified branch.

```
sgit update redis
```


## Development

Create a virtualenvrionment on your system.

Install all runtime dependencies, development dependencies and the package in local editable mode with

```
pip install -e ".[dev]"
```

To run all unit tests run `pytest` from the root folder.
