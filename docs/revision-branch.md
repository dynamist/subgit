# Revision: branch

If you want to specify the cloning and updating of a git repo based on a git branch you can define it with the following syntax.

```yaml
repos:
  pykwalify:
    url: git@github.com:Grokzen/pykwalify.git
    revision:
      branch: master
```

This will clone the git repo and for each `subgit pull` you make after the initial clone, it will do a git pull on the given branch to move your clone to the latest commit on this branch.

In the case you change the branch to a new one, it will fetch the latest commits for that other branch and do a git checkout of it locally.


## CLI

To update your git cloned repos to a new git revision, branch or tag use

```
subgit pull
```

In the case you have defined a branch that do not exists on the `origin remote` then you will get an error when running `subgit pull`. No checks is done at the time you set your branch.
