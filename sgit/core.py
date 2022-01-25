# -*- coding: utf-8 -*-

# python std lib
import logging
import os
import re
import sys

# sgit imports
from sgit.constants import *
from sgit.exceptions import *

# 3rd party imports
import git
import semver
from git import Repo, Git
from ruamel import yaml
from ruamel.yaml import Loader


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class Sgit():
    def __init__(self, config_file_path=None, answer_yes=False):
        self.answer_yes = answer_yes

        if not config_file_path:
            self.sgit_config_file_name = ".sgit.yml"

            self.sgit_config_file_path = os.path.join(
                os.getcwd(), self.sgit_config_file_name
            )
        else:
            self.sgit_config_file_name = os.path.basename(config_file_path)
            self.sgit_config_file_path = config_file_path

    def init_repo(self):
        """
        Algorithm:
            - Check if .sgit.yml exists
                - If exists:
                    - Exit out from script
                - If do not exists
                    - Write new initial empty file to disk
        """
        if os.path.exists(self.sgit_config_file_path):
            print(f"File '{self.sgit_config_file_name}' already exists on disk")
            return 1

        with open(self.sgit_config_file_path, "w") as stream:
            stream.write(DEFAULT_REPO_CONTENT)
            print(f'Successfully wrote new config file "{self.sgit_config_file_name}" to disk')

    def _get_config_file(self):
        if not os.path.exists(self.sgit_config_file_path):
            print("No .sgit.yml file exists in current CWD")
            sys.exit(1)

        with open(self.sgit_config_file_path, "r") as stream:
            return yaml.load(stream, Loader=Loader)
            # TODO: Minimal required data should be 'repos:'
            #       Raise error if missing from loaded config

    def _dump_config_file(self, config_data):
        """
        Writes the entire config file to the given disk path set
        in the method constructor.
        """
        with open(self.sgit_config_file_path, "w") as stream:
            yaml.dump(config_data, stream, indent=2, default_flow_style=False)

    def repo_list(self):
        config = self._get_config_file()
        repos = config.get("repos", {})

        print(f" ** All repos **")

        if not repos:
            print(f"  No repos found")
            return 1

        for repo_name, repo_data in repos.items():
            print(f"")
            print(f" - {repo_name}")
            print(f"    URL: {repo_data.get('clone-url')}")

            if "branch" in repo_data["revision"]:
                print(f"    Branch: {repo_data.get('revision', {}).get('branch', None)}")
            elif "tag" in repo_data["revision"]:
                print(f"    Tag: {repo_data.get('revision', {}).get('tag', None)}")
            else:
                raise SgitConfigException('No tag or "branch" key found inside "revision" block for repo "{name}')

    def repo_add(self, name, url, revision):
        if not name or not url or not revision:
            raise SgitConfigException(f'Name "{name}, url "{url}" or revision "{revision}" must be set')

        config = self._get_config_file()

        if name in config.get("repos", []):
            print(f'Repo with name "{name}" already exists in config file')
            return 1

        # TODO: It is bad that each repo will default to a branch type and not a tag type
        config["repos"][name] = {"clone-url": url, "revision": {"branch": revision}}

        self._dump_config_file(config)

        print(f'Successfully added new repo "{name}"')

    def repo_remove(self, name):
        if not name:
            raise SgitConfigException(f'Name "{name}" must be set to sometihng')

        config = self._get_config_file()

        if name not in config.get("repos", []):
            print(f'No repo with name "{name}" found in config file')
            return 1

        del config["repos"][name]

        self._dump_config_file(config)

        print(f'Removed repo "{name}" from config file')

    def repo_set(self, name, attrib, value):
        if not attrib or not value:
            raise SgitConfigException(f'Attrib "{attrib}" or "{value}" must be set')

        config = self._get_config_file()

        if name not in config.get("repos", []):
            print(f'Repo with name "{name}" not found in config file')
            return 1

        if attrib == "tag":
            del config["repos"][name]["revision"]["tag"]
            config["repos"][name]["revision"]["tag"] = value
            print(f'Set tag for repo "{name}" to -> "{value}"')
        elif attrib == "branch":
            del config["repos"][name]["revision"]["branch"]
            config["repos"][name]["revision"]["branch"] = value
            print(f'Set branch for repo "{name}" to -> "{value}"')
        elif attrib == "url":
            config["repos"][name]["clone-url"] = value
            print(f'Set git clone-url for repo "{name}" to -> "{value}"')
        else:
            print(f"Unsupported set attribute operation")
            return 1

        self._dump_config_file(config)

    def yes_no(self, question):
        print(question)

        if self.answer_yes:
            print(f"INFO: Automatically answer yes to question")
            return True

        answer = input("(y/n) << ")

        return answer.lower().startswith("y")

    def fetch(self, repos):
        """
        Runs "git fetch" on one or more git repos.

        To update all enabled repos send in None as value.

        To update a subset of repo names, send in them as a list of strings.
        A empty list of items will update no repos.
        """
        print(f"DEBUG: Repo fetch input - {repos}")

        config = self._get_config_file()

        repos_to_fetch = []

        if repos is None:
            for repo_name in config["repos"]:
                repos_to_fetch.append(repo_name)

        if isinstance(repos, list):
            for repo_name in repos:
                if repo_name in config["repos"]:
                    repos_to_fetch.append(repo_name)
                else:
                    print(f"WARNING: repo '{repo_name}' not found in configuration")

        print(f"INFO: repos to fetch: {repos_to_fetch}")

        if len(repos_to_fetch) == 0:
            print(f"No repos to fetch found")
            return 1

        for repo_name in repos_to_fetch:
            try:
                repo_path = os.path.join(os.getcwd(), repo_name)
                git_repo = Repo(repo_path)

                print(f"Fetching git repo '{repo_name}'")
                fetch_results = git_repo.remotes.origin.fetch()
                print(f"Fetching completed for repo '{repo_name}'")

                for fetch_result in fetch_results:
                    print(f" - Fetch result: {fetch_result.name}")
            except git.exc.NoSuchPathError:
                print(f"Repo {repo_name} not found on disk. You must update to clone it before fetching")
                return 1

        print(f"Fetching for all repos completed")
        return 0


    def repo_rename(self, from_name, to_name):
        print(f'DEBUG: Rename repo "{from_name}" to "{to_name}')

        config = self._get_config_file()

        current_repos = config.get("repos", [])

        if from_name == to_name:
            print(f"ERROR: from name and to name can't be the same value")
            return 1

        if to_name in current_repos:
            print(f"ERROR: Destination name already exists in config")
            return 2

        # Rename action
        config["repos"][to_name] = config["repos"][from_name]

        # Remove old repo name
        del config["repos"][from_name]

        self._dump_config_file(config)

        print(f'INFO: Renamed repo from "{from_name}" to "{to_name}"')

    def repo_enable(self, repo_name):
        """
        Will set the option `enable: true` for a given repo

        Returns 0 if enable repo was successfull
        Returns 1 if provided repo name was not found in config
        """
        print(f"DEBUG: Enable repo {repo_name}")

        config = self._get_config_file()

        current_repos = config.get("repos", [])

        if repo_name not in current_repos:
            print(f"ERROR: Repo name not found in config file")
            return 1

        config["repos"][repo_name]["enabled"] = True

        self._dump_config_file(config)

        print(f"INFO: Enabled repo Successfully")

    def repo_disable(self, repo_name):
        """
        Will set the option `disable: true` for a given repo

        Returns 0 if disable repo was successfull
        Returns 1 if provided repo name was not found in config
        """
        print(f"DEBUG: Enable repo {repo_name}")

        config = self._get_config_file()

        current_repos = config.get("repos", [])

        if repo_name not in current_repos:
            print(f"ERROR: Repo name not found in config file")
            return 1

        config["repos"][repo_name]["enabled"] = False

        self._dump_config_file(config)

        print(f"INFO: Disable repo Successfully")

    def _get_active_repos(self, config):
        """
        Helper method that will return only the repos that is enabled and active for usage
        """
        active_repos = []

        for repo_name, repo_data in config.get("repos", {}).items():
            if repo_data.get("enable", True):
                active_repos.append(repo_name)

        return active_repos

    def update(self, names):
        """
        To update all repos defined in the configuration send in names=None

        To update a subset of repos send in a list of strings names=["repo1", "repo2"]

        Algorithm:
            - If the folder do not exists
                - clone the repo with Repo.clone_from
                - Update the rev to specified rev
            - If the folder do exists
                - If working_tree has any changes in it
                    - Throw error about working tree has changes
                - If working tree is empty
                    - Reset the repo to the specified rev
        """
        print(f"DEBUG: Repo update - {names}")

        config = self._get_config_file()

        active_repos = self._get_active_repos(config)

        repos = []

        if len(active_repos) == 0:
            print(f"ERROR: There is no repos defined or enabled in the config")
            return 1

        if names is None:
            repos = config.get("repos", [])
            repo_choices = ", ".join(active_repos)

            answer = self.yes_no(f'Are you sure you want to update the following repos "{repo_choices}"')

            if not answer:
                print(f"User aborted update step")
                return 1
        elif isinstance(names, list):
            # Validate that all provided repo names exists in the config
            for name in names:
                if name not in active_repos:
                    choices = ", ".join(active_repos)
                    print(f'Repo with name "{name}" not found in config file. Choices are "{choices}"')
                    return 1

            # If all repos was found, use the list of provided repos as list to process below
            repos = names
        else:
            print(f"DEBUG: names {names}")
            raise SgitConfigException(f"Unsuported value type for argument names")

        if not repos:
            raise SgitConfigException(f"No valid repositories found")

        #
        ## Validation step across all repos to manipulate that they are not dirty
        ## or anything uncommited that would break the code trees.
        ##
        ## Abort out if any repo is bad.
        #

        has_dirty = False

        for name in repos:
            repo_path = os.path.join(os.getcwd(), name)

            # If the path do not exists then the repo can't be dirty
            if not os.path.exists(repo_path):
                continue

            repo = Repo(repo_path)

            ## A dirty repo means there is uncommited changes in the tree
            if repo.is_dirty():
                print(f'ERROR: The repo "{name}" is dirty and has uncommited changes in the following files')
                dirty_files = [item.a_path for item in repo.index.diff(None)]

                for file in dirty_files:
                    print(f" - {file}")

                has_dirty = True

        if has_dirty:
            print(f"\nERROR: Found one or more dirty repos. Resolve it before continue...")
            return 1

        #
        ## Repos looks good to be updated. Run the update logic for each repo in sequence
        #

        for name in repos:
            repo_path = os.path.join(os.getcwd(), name)
            revision = config["repos"][name]["revision"]

            if not os.path.exists(repo_path):
                clone_rev = revision["tag"] if "tag" in revision else revision["branch"]

                try:
                    repo = Repo.clone_from(
                        config["repos"][name]["clone-url"],
                        repo_path,
                        branch=clone_rev,
                    )
                    print(f'Successfully cloned repo "{name}" from remote server')
                except git.exc.GitCommandError as e:
                    # We assume that retcode 128 means you try to clone into a bare repo and we must
                    # attempt to clone it w/o a specific branch identifier.
                    if e.status == 128:
                        try:
                            repo = Repo.clone_from(
                                config["repos"][name]["clone-url"],
                                repo_path,
                            )
                            print(f'Successfully cloned into bare git repo "{name}" from remote server')
                        except Exception as e:
                            raise SgitException(f'Clone into bare git repo "{name}" failed, exception: {e}')
                except Exception as e:
                    raise SgitException(f'Clone "{name}" failed, exception: {e}')
            else:
                print(f"TODO: Parse for any changes...")
                # TODO: Check that origin remote exists

                repo = Repo(os.path.join(os.getcwd(), name))

                g = Git(os.path.join(os.getcwd(), name))

                # Fetch all changes from upstream git repo
                repo.remotes.origin.fetch()

                # How to handle the repo when a branch is specified
                if "branch" in revision:
                    print(f"DEBUG: Handling branch update case")

                    # Extract the sub tag data
                    branch_revision = revision["branch"]

                    # Ensure the local version of the branch exists and points to the origin ref for that branch
                    repo.create_head(f"{branch_revision}", f"origin/{branch_revision}")

                    # Checkout the selected revision
                    # TODO: This only support branches for now
                    repo.heads[branch_revision].checkout()

                    print(f'Successfully update repo "{name}" to latest commit on branch "{branch_revision}"')
                    print(f"INFO: Current git hash on HEAD: {str(repo.head.commit)}")
                elif "tag" in revision:
                    print("TODO: Handle tag update case")

                    # Fetch all tags from the git repo and order them by the date they was made.
                    # The most recent tag is first in the list
                    tags = [
                        str(tag)
                        for tag in reversed(
                            sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
                        )
                    ]
                    print(f"DEBUG: {tags}")

                    if len(tags) == 0:
                        raise SgitRepoException(f"Revision set to a tag, but no tags exists within the selected git repo '{name}'")

                    # Extract the sub tag data
                    tag_revision = revision["tag"]

                    # Special case if using the reserved tag keyword "latest"
                    if tag_revision == "latest":
                        print(f"DEBUG: Keyword 'latest' used for tag. Attempting to parse")

                        # Pre-process tags list by running tag-filter-regex to filter out unwanted tags from the list
                        tag_filter_regex = revision.get("tag-filter-regex", None)

                        if tag_filter_regex:
                            print(f"INFO: 'tag-regex-filter' option set for git repo {name}, filtering out unwanted tags based on regex")

                            if not isinstance(tag_filter_regex, list):
                                raise SgitConfigException(f"Value for option 'tag-filter-regex' must be a list and not {type(tag_filter_regex)}")

                            filtered_tags = []

                            for tag in tags:
                                for filter_regex in tag_filter_regex:
                                    print(f"DEBUG: Filtering tag '{tag}' against regex '{filter_regex}")
                                    if re.match(filter_regex, tag):
                                        filtered_tags.append(tag)
                                        break

                            print(f"INFO: filtered_tags result: {filtered_tags}")

                            # Set result back for next step in pre-processing
                            tags = filtered_tags

                        # Pre-process tags list by running tag-regex filtering on all values
                        tag_clean_regex = revision.get('tag-clean-regex', None)

                        if tag_clean_regex:
                            print(f"INFO: Option 'tag-clean-regex' set for repo {name}, filtering out tags based on regex")

                            if not isinstance(tag_clean_regex, list):
                                raise SgitConfigException(f"Value for option 'tag-clean-regex' must be a list and not {type(tag_clean_regex)}")

                            cleaned_tags = []

                            for tag in tags:
                                cleaned = False

                                for clean_regex in tag_clean_regex:
                                    print(f"DEBUG: Cleaning tag '{tag}' against regex '{clean_regex}")
                                    match_result = re.match(clean_regex, tag)
                                    if match_result:
                                        print(f"Clean match result hit: {match_result}")
                                        cleaned_tags.append(match_result.groups()[0])
                                        cleaned = True
                                        break

                                if not cleaned:
                                    cleaned_tags.append(tag)

                            print(f"INFO: Cleaned tags result: {cleaned_tags}")

                            tags = cleaned_tags

                        # supported "tag-order" values is "semver" and "time"
                        tag_order_option = revision.get("tag-order", "semver")

                        selected_tag = None

                        if tag_order_option == "time":
                            # Pick the first item from the pre-sorted tags list
                            selected_tag = tags[0]
                        elif tag_order_option == "semver":
                            # Special case as if we only have one tag we can't compare it to anything else
                            if len(tags) == 1:
                                selected_tag = tags[0]
                            else:
                                tmp_latest = tags[0]

                                for i, item in enumerate(tags):
                                    left = tmp_latest
                                    try:
                                        right = tags[i + 1]
                                    except IndexError:
                                        # We have itterated all possible values
                                        break

                                    print(f"DEBUG: Comparing {left} <--> {right}")

                                    compare_value = semver.compare(left, right)

                                    if compare_value == 1:
                                        tmp_latest = left
                                        print(f"Left is higher then right")
                                    elif compare_value == -1:
                                        tmp_latest = right
                                        print(f"Right is higher then left")
                                    else:
                                        print(f"DEBUG: tag values are the same")

                                print(f"DEBUG: tmp_latest {tmp_latest}")

                                selected_tag = tmp_latest
                        else:
                            raise SgitConfigException(f"Value for 'tag-order: {tag_order_option}' for repo {name} must be either 'semver' or 'time'")

                        tag_revision = selected_tag

                    if tag_revision in tags:
                        g.checkout(tag_revision)
                        print(f'INFO: Checked out tag "{tag_revision}" for repo "{name}"')
                        print(f"INFO: Current git hash on HEAD: {str(repo.head.commit)}")
                        print(f"INFO: Current commit summary on HEAD: {str(repo.head.commit.summary)}")
                    else:
                        print(f'ERROR: Specified tag "{tag_revision}" do not exists inside repo "{name}"')
                        print(f"")
                        print(f" - Available tags")

                        for tag in tags:
                            print(f"   - {tag}")
