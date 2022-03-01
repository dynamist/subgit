# -*- coding: utf-8 -*-

# python std lib
import logging
import os
import re
import sys
from subprocess import PIPE, Popen

# sgit imports
from sgit.constants import *
from sgit.enums import *
from sgit.exceptions import *

# 3rd party imports
import git
import packaging
from git import Repo, Git
from packaging import version
from packaging.specifiers import SpecifierSet
from ruamel import yaml


log = logging.getLogger(__name__)


class Sgit():
    def __init__(self, config_file_path=None, answer_yes=False):
        self.answer_yes = answer_yes

        if not config_file_path:
            self.sgit_config_file_name = ".sgit.yml"

            self.sgit_config_file_path = os.path.join(
                os.getcwd(),
                self.sgit_config_file_name,
            )
        else:
            self.sgit_config_file_name = os.path.basename(config_file_path)
            self.sgit_config_file_path = config_file_path

    def init_repo(self, repo_name=None, repo_url=None):
        """
        If repo_name & repo_url is set to a string value, it will be attempted to be added to the initial
        .sgit.yml config file as the first repo in your config. If these values is anything else the initial
        config vill we written as empty.
        """
        if os.path.exists(self.sgit_config_file_path):
            log.error(f"File '{self.sgit_config_file_name}' already exists on disk")
            return 1

        tmp_config = DEFAULT_REPO_DICT

        if isinstance(repo_name, str) and isinstance(repo_url, str):
            log.info(f"Adding initial git repo '{repo_name}' with url '{repo_url}' to your config")
            tmp_config["repos"][repo_name] = {"url": repo_url, "revision": {"branch": "master"}}

        with open(self.sgit_config_file_path, "w") as stream:
            self._dump_config_file(tmp_config)
            log.info(f'Successfully wrote new config file "{self.sgit_config_file_name}" to disk')

    def _get_config_file(self):
        if not os.path.exists(self.sgit_config_file_path):
            log.error("No .sgit.yml file exists in current CWD")
            sys.exit(1)

        with open(self.sgit_config_file_path, "r") as stream:
            return yaml.load(stream, Loader=yaml.Loader)
            # TODO: Minimal required data should be 'repos:'
            #       Raise error if missing from loaded config

    def _dump_config_file(self, config_data):
        """
        Writes the entire config file to the given disk path set
        in the method constructor.
        """
        with open(self.sgit_config_file_path, "w") as stream:
            yaml.dump(config_data, stream, indent=2, default_flow_style=False)

    def repo_status(self):
        config = self._get_config_file()
        repos = config.get("repos", {})

        if not repos:
            print(f"  No repos found")
            return 1

        for repo_name, repo_data in repos.items():
            print(f"{repo_name}")
            print(f"  Url: {repo_data.get('url', 'NOT SET')}")

            repo_disk_path = os.path.join(os.getcwd(), repo_name)
            print(f"  Disk path: {repo_disk_path}")

            try:
                repo = Repo(repo_disk_path)
                cloned_to_disk = True
            except git.exc.NoSuchPathError:
                cloned_to_disk = False
            
            print(f"  Cloned: {'Yes' if cloned_to_disk else 'No'}")

            if cloned_to_disk:
                file_cwd = os.path.join(os.getcwd(), repo_name, ".git/FETCH_HEAD")

                if os.path.exists(file_cwd):
                    command = f"stat -c %y {file_cwd}"
                    process = Popen(command, stdout=PIPE, stderr=None, shell=True)
                    output, stderr = process.communicate()
                    parsed_output = str(output).replace('\\n', '')
                    print(f"  Last pull/fetch: {parsed_output}")
                else:
                    print(f"  Last pull/fetch: Repo has not been pulled or fetch since initial clone")
            else:
                print(f"  Last pull/fetch: UNKNOWN repo not cloned to disk")

            if cloned_to_disk:
                repo = Repo(repo_disk_path)
                print(f"  Repo is dirty? {'Yes' if repo.is_dirty() else 'No'}")
            else:
                print(f"  Repo is dirty? ---")

            branch = repo_data['revision'].get('branch', '---')
            commit = repo_data['revision'].get('commit', '---')
            tag = repo_data['revision'].get('tag', '---')

            print(f"  Revision:")

            print(f"    branch: {branch}")
            if branch != "---":
                if branch in repo.heads:
                    commit_hash = str(repo.heads[branch].commit)
                    commit_message = str(repo.heads[branch].commit.summary)
                    has_new = repo.remotes.origin.refs["master"].commit != repo.heads[branch].commit
                else:
                    commit_hash = "Local branch not found"
                    commit_message = "Local branch not found"
                    has_new = "---"

                print(f"      commit hash: {commit_hash}")
                print(f"      commit message: '{commit_message}'")
                print(f"      branch exists in origin? {branch in repo.remotes.origin.refs}")
                print(f"      has newer commit in origin? {has_new}")

            print(f"    commit: {commit}")
            if commit != "---":
                print(f"FIXME: Not implemented yet")

            # Extract tag from inner value if that is set
            #  {revision: {tag: {select: {value: foo}}}}
            if isinstance(tag, dict):
                tag = tag["select"]

                if isinstance(tag, dict):
                    tag = tag["value"]

            print(f"    tag: {tag}")

            if tag != "---":
                if tag in repo.tags:
                    commit_hash = str(repo.tags[tag].commit)
                    commit_summary = str(repo.tags[tag].commit.summary)
                else:
                    commit_hash = "Tag not found"
                    commit_summary = "---"

                print(f"      commit hash: {commit_hash}")
                print(f"      commit message: '{commit_summary}'")

            print(f"")

    def yes_no(self, question):
        print(question)

        if self.answer_yes:
            log.info(f"--yes flag set, automatically answer yes to question")
            return True

        answer = input("(y/n) << ")

        return answer.lower().startswith("y")

    def fetch(self, repos):
        """
        Runs "git fetch" on one or more git repos.

        To fetch all enabled repos send in None as value.

        To fetch a subset of repo names, send in them as a list of strings.
        
        A empty list of items will not fetch any repo.
        """
        log.debug(f"repo fetch input - {repos}")

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
                    log.warning(f"repo '{repo_name}' not found in configuration")

        log.info(f"repos to fetch: {repos_to_fetch}")

        if len(repos_to_fetch) == 0:
            log.error(f"No repos to fetch found")
            return 1

        missing_any_repo = False

        for repo_name in repos_to_fetch:
            try:
                repo_path = os.path.join(os.getcwd(), repo_name)
                git_repo = Repo(repo_path)
            except git.exc.NoSuchPathError:
                log.error(f"Repo {repo_name} not found on disk. You must pull to do a initial clone before fetching can be done")
                missing_any_repo = True

        if missing_any_repo:
            return 1

        for repo_name in repos_to_fetch:
            repo_path = os.path.join(os.getcwd(), repo_name)
            git_repo = Repo(repo_path)

            log.info(f"Fetching git repo '{repo_name}'")
            fetch_results = git_repo.remotes.origin.fetch()
            log.info(f"Fetching completed for repo '{repo_name}'")

            for fetch_result in fetch_results:
                log.info(f" - Fetch result: {fetch_result.name}")

        log.info(f"Fetching for all repos completed")
        return 0

    def _get_active_repos(self, config):
        """
        Helper method that will return only the repos that is enabled and active for usage
        """
        active_repos = []

        for repo_name, repo_data in config.get("repos", {}).items():
            if repo_data.get("enable", True):
                active_repos.append(repo_name)

        return active_repos

    def pull(self, names):
        """
        To pull all repos defined in the configuration send in names=None

        To pull a subset of repos send in a list of strings names=["repo1", "repo2"]
        """
        log.debug(f"Repo pull - {names}")

        config = self._get_config_file()

        active_repos = self._get_active_repos(config)

        repos = []

        if len(active_repos) == 0:
            log.error(f"There is no repos defined or enabled in the config")
            return 1

        if names is None:
            repos = config.get("repos", [])
            repo_choices = ", ".join(active_repos)

            answer = self.yes_no(f"Are you sure you want to 'git pull' the following repos '{repo_choices}'")

            if not answer:
                log.warning(f"User aborted pull step")
                return 1
        elif isinstance(names, list):
            # Validate that all provided repo names exists in the config
            for name in names:
                if name not in active_repos:
                    choices = ", ".join(active_repos)
                    log.error(f'Repo with name "{name}" not found in config file. Choices are "{choices}"')
                    return 1

            # If all repos was found, use the list of provided repos as list to process below
            repos = names
        else:
            log.debug(f"Names {names}")
            raise SgitConfigException(f"Unsuported value type for argument names")

        if not repos:
            raise SgitConfigException(f"No valid repositories found")

        # Validation step across all repos to manipulate that they are not dirty
        # or anything uncommited that would break the code trees.
        #
        # Abort out if any repo is bad.

        has_dirty = False

        for name in repos:
            repo_path = os.path.join(os.getcwd(), name)

            # If the path do not exists then the repo can't be dirty
            if not os.path.exists(repo_path):
                continue

            repo = Repo(repo_path)

            # A dirty repo means there is uncommited changes in the tree
            if repo.is_dirty():
                log.error(f'The repo "{name}" is dirty and has uncommited changes in the following files')
                dirty_files = [item.a_path for item in repo.index.diff(None)]

                for file in dirty_files:
                    log.info(f" - {file}")

                has_dirty = True

        if has_dirty:
            log.error(f"\nFound one or more dirty repos. Resolve it before continue...")
            return 1

        # Repos looks good to be pulled. Run the pull logic for each repo in sequence

        for name in repos:
            log.info("")

            repo_path = os.path.join(os.getcwd(), name)
            repo_config = config["repos"][name]
            revision = repo_config["revision"]

            if not os.path.exists(repo_path):
                clone_rev = revision["tag"] if "tag" in revision else revision["branch"]
                clone_url = repo_config.get("url", None)

                if not clone_url:
                    raise SgitConfigException(f"Missing required key 'url' on repo '{name}'")

                try:
                    # Cloning a repo w/o a specific commit/branch/tag it will clone out whatever default
                    # branch or where the origin HEAD is pointing to. After we clone we can then move our
                    # repo to the correct revision we want.
                    repo = Repo.clone_from(
                        config["repos"][name]["url"],
                        repo_path,
                    )
                    log.info(f'Successfully cloned repo "{name}" from remote server')
                except Exception as e:
                    raise SgitException(f'Clone "{name}" failed, exception: {e}')

            log.debug(f"TODO: Parse for any changes...")
            # TODO: Check that origin remote exists

            repo = Repo(os.path.join(os.getcwd(), name))

            g = Git(os.path.join(os.getcwd(), name))

            # Fetch all changes from upstream git repo
            repo.remotes.origin.fetch()

            # How to handle the repo when a branch is specified
            if "branch" in revision:
                log.debug(f"Handling branch pull case")

                # Extract the sub tag data
                branch_revision = revision["branch"]

                # Ensure the local version of the branch exists and points to the origin ref for that branch
                repo.create_head(f"{branch_revision}", f"origin/{branch_revision}")

                # Checkout the selected revision
                # TODO: This only support branches for now
                repo.heads[branch_revision].checkout()

                log.info(f'Successfully pull repo "{name}" to latest commit on branch "{branch_revision}"')
                log.info(f"Current git hash on HEAD: {str(repo.head.commit)}")
            elif "tag" in revision:
                #
                # Parse and extract out all relevant config options and determine if they are nested
                # dicts or single values. The values will later be used as input into each operation.
                #
                tag_config = revision["tag"]

                if isinstance(tag_config, str):
                    # All options should be set to default'
                    filter_config = []
                    order_algorithm = OrderAlgorithms.SEMVER
                    order_config = None
                    select_config = tag_config
                    select_method = SelectionMethods.SEMVER
                elif isinstance(tag_config, dict):
                    # If "filter" key is not specified then we should not filter anything and keep all values
                    filter_config = tag_config.get("filter", [])

                    # If we do not have a list, convert it internally first
                    if isinstance(filter_config, str):
                        filter_config = [filter_config]

                    if not isinstance(filter_config, list):
                        raise SgitConfigException(f"filter option must be a list of items or a single string")

                    order_config = tag_config.get("order", None)
                    if order_config is None:
                        order_algorithm = OrderAlgorithms.SEMVER
                    else:
                        order_algorithm = OrderAlgorithms.__members__.get(order_config.upper(), None)

                        if order_algorithm is None:
                            raise SgitConfigException(f"Unsupported order algorithm chose: {order_config.upper()}")

                    select_config = tag_config.get("select", None)
                    select_method = None
                    if select_config is None:
                        raise SgitConfigException(f"select key is required in all tag revisions")

                    log.debug(f"select_config: {select_config}")

                    # We have sub options to extract out
                    if isinstance(select_config, dict):
                        select_method_value = select_config["method"]
                        select_config = select_config["value"]
                        
                        log.debug(f"select_method: {select_method_value}")

                        select_method = SelectionMethods.__members__.get(select_method_value.upper(), None)

                        if select_method is None:
                            raise SgitConfigException(f"Unsupported select method chosen: {select_method_value.upper()}")
                    else:
                        select_method = SelectionMethods.SEMVER
                else:
                    raise SgitConfigException(f"Key revision.tag for repo {name} must be a string or dict object")

                log.debug(f"{filter_config}")
                log.debug(f"{order_config}")
                log.debug(f"{order_algorithm}")
                log.debug(f"{select_config}")
                log.debug(f"{select_method}")

                # Main tag parsing logic

                git_repo_tags = [
                    tag for tag in repo.tags
                ]
                log.debug(f"Raw git tags from git repo {git_repo_tags}")

                filter_output = self._filter(git_repo_tags, filter_config)

                # # FIXME: If we choose time as sorting method we must convert the data to a new format
                # #        that the order algorithm allows.
                # if order_algorithm == OrderAlgorithms.TIME:
                #     pass

                order_output = self._order(filter_output, order_algorithm)
                select_output = self._select(order_output, select_config, select_method)
                log.debug(select_output)

                if not select_output:
                    raise SgitRepoException(f"No git tag could be parsed out with the current repo configuration")

                log.info(f"Attempting to checkout tag '{select_output}' for repo '{name}'")

                # Otherwise atempt to checkout whatever we found. If our selection is still not something valid
                # inside the git repo, we will get sub exceptions raised by git module.
                g.checkout(select_output)

                log.info(f"Checked out tag '{select_output}' for repo '{name}'")
                log.info(f"Current git hash on HEAD: {str(repo.head.commit)}")
                log.info(f"Current commit summary on HEAD in git repo '{name}': ")
                log.info(f"  {str(repo.head.commit.summary)}")

    def _filter(self, sequence, regex_list):
        """
        Given a sequence of git objects, clean them against all regex items in the provided regex_list.

        Cleaning one item in the seuqence means that we can extract out any relevant information from our sequence
        in order to make further ordering and selection at later stages.

        The most basic example is to make semver comparisons we might need to remove prefixes and suffixes
        from the tag name in order to make a semver comparison.

        v1.0.0 would be cleaned to 1.0.0, and 1.1.0-beta1 would be cleaned to 1.1.0 and we can then make a semver
        comparison between them in order to find out the latest tag item.
        """
        filtered_sequence = []

        log.debug(f"Running clean step on data")

        if not isinstance(regex_list, list):
            raise SgitConfigException(f"sequence for clean step must be a list of items")

        if not isinstance(regex_list, list):
            raise SgitConfigException(f"regex_list for clean step must be a list of items")

        # If we have no regex to filter against, then return original list unaltered
        if len(regex_list) == 0:
            return sequence

        for item in sequence:
            for filter_regex in regex_list:
                if not isinstance(filter_regex, str):
                    raise SgitConfigException(f"ERROR: filter regex must be a string")

                # A empty regex string is not valid
                if filter_regex.strip() == "":
                    raise SgitConfigException(f"ERROR: Empty regex filter string is not allowed")

                log.debug(f"Filtering item '{str(item)}' against regex '{filter_regex}")

                match_result = re.match(filter_regex, str(item))

                if match_result:
                    log.debug(f"Filter match result hit: {match_result}")

                    # If the regex contains a group that is what we want to extract out and
                    # add to our filtered output list of results
                    if len(match_result.groups()) > 0:
                        filtered_sequence.append(match_result.groups()[0])
                    else:
                        filtered_sequence.append(item)

                    break

        log.debug(f"Filter items result: {filtered_sequence}")

        return filtered_sequence

    def _order(self, sequence, order_method):
        """
        Given a sequence of git objects, order them based on what ordering algorithm selected.

        Some algorithms might require additional information in order to perform the ordering properly,
        in these cases each item in the sequence should be a tuple where the first value is the key or primary
        data we want to sort on, like tag name. But the second and/or third item in the tuple can be for example
        a timestamp or other metadata that we need to use within our algorithm to order them properly.

        Supports OrderAlgorithm methods: ALPHABETICAL, TIME, SEMVER

        If unsupported order_method is specified, it will thro SgitConfigException

        Returns a new list with the sorted sequence of items
        """
        ordered_sequence = []

        if order_method == OrderAlgorithms.SEMVER:
            log.debug(f"Ordering sequence of items by PEP440 SEMVER logic")
            log.debug(sequence)

            # By using packages module and Version class we can properly compare semver
            # versions with PEP440 compatible version compare
            ordered_sequence = list(sorted(sequence, key=lambda x: version.Version(str(x))))
        elif order_method == OrderAlgorithms.TIME:
            log.debug(f"Ordering sequence of items by TIME they was created, input:")
            log.debug(sequence)

            # When sorting by time the latest item in the sequence with the highest or most recent time
            # will be on index[0] in the returned sequence
            ordered_sequence = list(sorted(sequence, key=lambda t: t[1]))
        elif order_method == OrderAlgorithms.ALPHABETICAL:
            log.debug(f"Order sequence of items by ALPHABETICAL string order")
            log.debug(sequence)

            # By default sorted will do alphabetical sort
            ordered_sequence = list(sorted(sequence))
        else:
            raise SgitConfigException(f"Unsupported ordering algorithm selected")

        log.debug(f"Ordered sequence result: {ordered_sequence}")

        return ordered_sequence

    def _select(self, sequence, selection_query, selection_method):
        """
        Given a sequence of objects, perform the selection based on the selection_method and the
        logic that it implements.

        Supported selection methods: SEMVER, EXACT

        If unsupported selection_method is specified, it will throw SgitConfigException

        SEMVER: It will run you selection against the sequence of items and with a library supporting
                PEP440 semver comparison logic. Important note here is that it will take the highest
                version depending on the previous ordering that still fits the semver version check.

                Given a sequence of 1.1.0, 1.0.0, 0.9.0 and a selection of >= 1.0.0, it will select 1.1.0

                Given a sequence of 0.9.0, 1.0.0, 1.1.0 and a selection of >= 0.9.0, it will select 0.9.0
                as that item is first in the sequence that matches the query.

                Two special keywords exists, first and last. First will pick the first item in the sequence
                and last will pick the last item in the sequence. Combining this with different ordering logics
                we can get a bit more dynamic selection options.

        EXACT: This matching algorithm is more of a textual exact comparison that do not use any semver of
               comparison between items in the sequence. In the case you want to point to a specific commit
               that do not have any general semver information or data in it you should use this method.
        """
        if selection_method == SelectionMethods.SEMVER:
            if selection_query == "last":
                return sequence[-1]
            elif selection_query == "first":
                return sequence[0]
            else:
                log.debug(f"Selection query")

                try:
                    spec = SpecifierSet(selection_query)

                    filtered_versions = list(
                        spec.filter([str(item) for item in sequence]),
                    )

                    log.debug(f"filtered_versions")
                    log.debug(filtered_versions)

                    return filtered_versions[-1]
                except packaging.specifiers.InvalidSpecifier:
                    log.warning(f"WARNING: Invalid SEMVER select query. Falling back to EXCAT matching of value")
                    selection_method = SelectionMethods.EXACT
        
        if selection_method == SelectionMethods.EXACT:
            for item in sequence:
                if str(item) == selection_query:
                    return item

            # Query not found in sequence, return None
            return None
        
        if selection_method not in SelectionMethods.__members__:
            raise SgitConfigException(f"Unsupported select algorithm selected")