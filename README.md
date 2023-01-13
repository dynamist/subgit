# Subgit

The name came originally from "Submodule Git", or more commonly "Sub Git".

The main purpose of this tool is to be used as a sync for cases to pull together a set of different Git repos into a deterministic directory tree. It is used to collect various individual parts into a whole.

The main two advantages over other solutions is that when compared to the normal git submodules, you can more easily specify and avoid having to commit into your tree every single update that you want to have in your subgit checkout. In a submodule solution where you want to update and track the current and latest commit for the maste branch, you do not have to update your configuration file each time you make a new commit in the child repo. In the cases where you are pointing to tags and stable releases of a software, there is not much difference. When comparing to other tools that manipulates and pulls in each remote repos entire tree into your tree, this tool avoids that and dont care about that scenario. The only file you have to commit into a repo that you want sub repos to be exposed to is the `.subgit.yml` config file.

This tool has been primarly constructed to be a part inside a CI/CD solution where you want to in a build step, clone the repo that contains the `.subgit.yml` config file, clone out whatever branches or tags for all the child repos and then perform some action or build step or test or similar function while using all of the repos from one spot.

In the event of you having a configuration file with another name than `.subgit.yml`, you can easily add the -c, --conf flag after the sub command in the command to point to a optional configuration file.

```bash
subgit pull -c path/to/conf-file
```

## Usage


### !!WARNING!!

Subgit do not leave any guarantees that it will NOT MODIFY or THROW AWAY any local changes or modifications done to the git repo that it checks out and handles. Subgit is `NOT` in any way capable of commiting any changes or pushing any changes to your git remotes. This tool is only intended to be able to pull in and together a set of other git repos into one folder.

In addition to `subgit`, you will also get an legacy alias `sgit` command.

In the future there will also be support for integrating this tool directly into git by running `git sub [...]`. This makes it more transparent to use with any other git command.


### Quickstart

Install the tool with `pip install subgit`. The tool requires `python>=3.8.0`, but we always recommend the latest major release as standard.

Create a temporary folder where you want your sub repos to be located

```bash
mkdir /tmp/subgit; cd /tmp/subgit
```

Initialize an empty `.subgit.yml` config file.

For compatibility we will support either naming the config file `.subgit.yml` and `.sgit.yml` until *1.0.0* release and at that time this support will be dropped.

```bash
subgit init

# or optionally you can specify the initial repo and clone url you want to be added with
subgit init pykwalify git@github.com:Grokzen/pykwalify.git
```

Inspect the content by looking inside the `.subgit.yml` config file

```bash
cat .subgit.yml

# This will show the default config in an empty config file
repos: { }
```

To add any number of git repos that you want to clone by manually editing the `.subgit.yml` configuration file.

Next step is to make the initial git clone/pull of all repos in the config file and move the repo to the specified revision. Running `subgit pull` command without any arguments will update all repos defined in the configuration file. If your repo is not present on disk it will make a initial `git clone` before moving to your selected revision.

```bash
subgit pull

# Or you can pull a specific repo from your config file.
subgit pull pykwalify
```

Subgit relies on your own ssh config or other git config is properly setup and configured in sucha way that you can clone the git repo without having to specify any other credentials or similar inside the git repo.

You can view a summary of your current repo and config state by running `subgit status`


## Fetch changes in a repo

If you want to `git fetch` all or a subset of git repos in your config then you can use the `subgit fetch` command. The benefit of doing a fetch is that you can fetch home all changes to a set of git repos but you do not have to update and move each repo to a new commit. In general git operations, it is always more safe to run `git fetch` before you do a checkout or `git pull` to update your local cloned repos. This allows you to inspect the changes incomming before commiting to pulling them.

The fetch command supports the selection of either all repos or a subset of repos. The fetch command will never prompt the user asking if they want to do a update as fetch is considered a non-descrutive command.

```bash
# Fetch all repos in sequence
subgit fetch

# Fetch one specified repo
subgit fetch pykwalify
```

## Delete pulled repos

You can delete local copies of your repos by using `subgit delete` command. This will only remove your repos locally, also only if they're considered 'clean'. This means that there are no commited changes or untracked files. You will get no explicit warning about what changes makes the repos 'dirty', except the specific repo which contain the changes.

The delete command supports the selection of either all repos or a subset of repos.

```bash
# Delete all repos in sequence
subgit delete

# Delete one specified repo
subgit delete pykwalify
```

## Import repos from Github or Gitlab

You can import a list of repos and create a new or overwrite an existing configuration file. Getting access to this command, two things need to be prepared. If these requirements are not met, the command will return an error and exit.

### Authentication for github cli

Download the latest release for github cli from here https://github.com/cli/cli/releases/ depending on your system. Once installed you should have access to `gh` command from your terminal.

Login to your github account with `gh auth login`. To verify you have correct access you can run `gh repo list` and it should list your personal github repos.

### Authentication for gitlab cli

Install python-gitlab from: https://python-gitlab.readthedocs.io/en/stable/

Next generate a new private API token for your account in gitlab. Create one here https://gitlab.com/-/profile/personal_access_tokens and set it to `readonly permissions` for everything including API access. 

Export your token in your terminal with `export GITLAB_PRIVATE_TOKEN=<YOUR TOKEN>` and it will allow for api access. Test this by running `gitlab projects list`

```bash
# Import all repos from github and write them to '.subgit.yml'
subgit import github <YOUR_USERNAME>

# Import all repos from gitlab and write them to '.subgit.yml'
subgit import gitlab <YOUR_USERNAME>

# You can redirect the output to another file with -o flag
subgit import github <YOUR_USERNAME> -o .some-other-file.yml
```

## Reset changed repos

You can reset repos in which changes have been made such as new files or new commits using `subgit reset` command. Using no particular option, `subgit reset` will reset the index to the origin pointer/reference. I will compare your working directory to that of the remote. If there are no changes, it will simply tell you that the current repo is clean. If there are any untracked files (files that are not added or commited) the '--hard' flag has to be appended to the command in order to force a reset.

```bash
# Reset all repos in sequence if they are dirty
subgit reset

# Reset one specified repo if it's dirty
subgit reset pykwalify
```

## Clean changed repos

With 'subgit clean' you can clean a repo from dirty files if 'subgit reset' hasn't done the job. By using 'subgit clean' you have a variety of options. Either use '--force' flag to only delete untracked files, without recursively removing untracked directories. Or append the '-d' flag in addition to '--force' to also remove directories. There is also a '--dry-run' flag that only shows you what would be removed, if the command was successfully executed.

```bash
# Clean all dirty repos from untracked files in sequence. (Skips directories)
subgit clean --force

# Clean all dirty repos from untracked files and directories.
subgit clean --force -d

# Cleans 'pykwalify' if it it dirty
subgit clean pykwalify --force -d

# Shows only what would be done if run successfully
subgit clean pykwalify --force -d --dry-run
```

Create a new git branch from the `master` branch and commit all changes you want to contribute in there. After your work is complete submit a Merge Request on gitlab back to the `master` branch. Ask a collegue for review and approval of the changes. Also if you are not he maintainer or your reviewer is not the maintainer, it is always good to ping and ask that person as well before mergin big changes. Smaller changes or fixes do not require this, but it is always encouraged to do this for all MR:s.

Requirement for a merge request

- Pytests should always pass and be green
- Any gitlab actions or PR specific tests/validation shold be green
- No merge conflicts with master branch, if you have then you either merge master into your branch and resolve conflicts, or you rebase your branch ontop of master branch
- Always do basic useability tests with most common commands as tests do not always show errors with everything
 

### Run unitest suite & Tox

To run all unit tests run `pytest` from the root folder. It will use your default python environment you are in right now.

We use tox to run multi python python tests to validate our test suite works our supported python version range.

Tox is installed in the pip extras block `.[test]`. To run all tests/linters against all versions simply run `tox` from your cli. To run a specific python version run `tox -e py310`. Most linux distros do not have all python versions installed by default.

This guide https://linuxize.com/post/how-to-install-python-3-8-on-ubuntu-18-04/ can help you to install older python versions either from dead-snakes repos or from source code.


### Extra development option flags

You can currently use the following envroinment flags `DEBUG=1` to get additional debugging and detailed information about any uncaught exceptions and detailed information about cli flags etc.

To get into a PDB debugger on any uncaught exceptions you can set the environment flag `PDB=1` and that will take you into a pdb debugger at the cli exit point so you can dig into any issues you might have.


## Python support guidelines

We follow the method of always suporting the latest released major version of python and two major versions back. This gives us backwards compatibility for about 2-3 years depending on the release speed of new python versions.

When a new major version is incorporated, tested and validated it works as expected and that dependencies is not broken, the update for new python version support should be released with the next major version of subgit. A major python version should never be dropped in a minor version update.

Python 2.7 is EOL and that version will not be supported moving forward.


## Build and publish a release to pypi

Ensure that you have updated all version tags to the desired version number for the next release. Either update the minor release or update the major release depending on the changes introduced within this release. Note that all support documents like releasenotes and other help documents must be completed and updated before this these build steps should be done. Once the build is uploaded to pypi it can't be reuploaded with a new build without bumping the version number again.

Create a fresh virtualenv. Install required build dependencies. Build the pckages

```bash
python -m pip install --upgrade setuptools wheel twine

# Remove the old dist/ folder to avoid collisions and reuploading existing releases
rm -r dist/

# Generate the source build and wheels build
python setup.py sdist bdist_wheel
````

Test and verify package can be installed locally within the virtualenv and that basic usage test cases works as expected and that simple cli oppreations like `subgit --help` and `subgit pull` and `subgit status` etc works as expected.

Next step is to test upload the release to the test-pypi server to ensure that the package will be accepted by pypi official server. Note that this step requires you to have a valid test-pypi account over at https://test.pypi.org/ and that you have the permissions to manage and upload the subgit shared project. If you do not have these things setup, please talk to the repo maintaner to setup this.

To upload the previous built dist packages to pypi run

```bash
python -m twine upload --repository testpypi dist/*
````

Input your username + password to the prompt. Note that username is case sensetive.

Validate your release was uploaded correct by visiting https://test.pypi.org/manage/project/subgit/ and look for the version number you uploaded. If this looks good and works then continue to upload the final release to regular pypi.org.

```bash
# Upload to pypi.org
python -m twine upload dist/*
````

Input your username + password but this time for your account on pypi.org and NOT test.pypi.org. These are two separate accounts. Same here, validate the build by going to https://pypi.org/manage/project/subgit/ and once these files is uploaded they are published and can't be rebuilt/replaced w/o making a post fix release. Read up onn python.org own release documentation for those steps.

Finally you should create the git tag for the git commit that you built. Run `git tag <semver-version>` to make the tag and push them with `git push --tags` to publish the tag. Rembmer to only do tags on the master branch.


## Project details

|   |   |
|---|---|
| python support         | 3.8, 3.9, 3.10, 3.11 |
| Source code            | https://github.com/dynamist/subgit |
| Changelog              | https://github.com/dynamist/subgit/blob/master/CHANGELOG.md |
| Issues                 | https://github.com/dynamist/subgit/issues |
| Projects page          | https://github.com/dynamist/subgit/projects/1
| pypi                   | https://pypi.python.org/pypi/subgit/ |
| License                | `Apache-2.0` https://github.com/dynamist/subgit/blob/master/LICENSE |
| Copyright              | `Copyright (c) 2019-2023 Dynamist AB` |
| git repo               | `git@github.com:dynamist/subgit.git` |
| install stable         | `pip install subgit` |
