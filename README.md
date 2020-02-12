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
