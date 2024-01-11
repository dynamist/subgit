# -*- coding: utf-8 -*-

# python std lib
import logging
import os
import re
import shutil
import sys
from multiprocessing import Pool
from pathlib import Path
from subprocess import PIPE, Popen  # nosec-B404

# 3rd party imports
import git
import packaging
from git import Git, Repo
from packaging import version
from packaging.specifiers import SpecifierSet
from ruamel import yaml

# subgit imports
from subgit.constants import *
from subgit.enums import *
from subgit.exceptions import *
from subgit.repo import SubGitRepo
from subgit.utils import bool_to_str


log = logging.getLogger(__name__)


def run_cmd(cli_command):
    process = Popen(
        cli_command,
        stdout=PIPE,
        stderr=None,
        shell=True,
    ) # nosec-B602
    output, stderr = process.communicate()

    return output, stderr


class SubGit():
    def __init__(self, config_file_path=None, answer_yes=False):
        self.answer_yes = answer_yes
        self.config_file_path = config_file_path

        if config_file_path:
            self.subgit_config_file_name = Path(config_file_path).name
            self.subgit_config_file_path = Path(config_file_path).resolve()
        else:
            self.subgit_config_file_name = ".subgit.yml"
            self.subgit_config_file_path = Path.cwd() / ".subgit.yml"

    def _resolve_recursive_config_path(self):
        """
        Looks for either .sgit.yml or .subgit.yml recursively
        """
        if not self.config_file_path:
            # Get the CWD where you execute the script from
            path = Path().cwd()

            while True:
                # Try to find the old config filename
                self.subgit_config_file_name = ".sgit.yml"
                self.subgit_config_file_path = path / self.subgit_config_file_name

                if self.subgit_config_file_path.exists():
                    log.warning("WARNING: using filename .sgit.yml will be deprecated in the future. Please convert it to .subgit.yml")
                    break

                # If old file do not exists then try the new filename
                self.subgit_config_file_name = ".subgit.yml"
                self.subgit_config_file_path = path / self.subgit_config_file_name

                if self.subgit_config_file_path.exists():
                    break

                # If we reach root folder then we should abort out
                if path == Path("/"):
                    log.critical("Unable to find a config file in any directory...")
                    sys.exit(1)

                path = path.parent.absolute()
                os.chdir(path)
                log.debug(f"Next iteration... Updated cwd path to {path}")

            log.info(f"Found config file...{self.subgit_config_file_path}")
            log.debug(self.subgit_config_file_name)
            log.debug(self.subgit_config_file_path)
        else:
            self.subgit_config_file_name = Path(self.config_file_path).name
            self.subgit_config_file_path = Path(self.config_file_path).resolve()

    def init_repo(self, repo_name=None, repo_url=None):
        """
        If repo_name & repo_url is set to a string value, it will be attempted to be added to the initial
        .subgit.yml config file as the first repo in your config. If these values is anything else the initial
        config vill we written as empty.
        """
        if self.subgit_config_file_path.exists():
            log.error(f"File '{self.subgit_config_file_name}' already exists on disk")
            return 1

        tmp_config = DEFAULT_REPO_DICT

        if isinstance(repo_name, str) and isinstance(repo_url, str):
            log.info(f"Adding initial git repo '{repo_name}' with url '{repo_url}' to your config")
            tmp_config["repos"].append({
                "name": repo_name,
                "url": repo_url,
                "revision": {"branch": "master"}
            })

        self._dump_config_file(tmp_config)
        log.info(f'Successfully wrote new config file "{self.subgit_config_file_name}" to disk')

    def _get_config_file(self):
        if not self.subgit_config_file_path.exists():
            log.error(f"No {self.subgit_config_file_path} file exists in current CWD")
            sys.exit(1)

        with open(self.subgit_config_file_path, "r") as stream:
            return yaml.load(
                stream,
                Loader=yaml.Loader,
            )
            # TODO: Minimal required data should be 'repos:'
            #       Raise error if missing from loaded config

    def _dump_config_file(self, config_data):
        """
        Writes the entire config file to the given disk path set
        in the method constructor.
        """
        with open(self.subgit_config_file_path, "w") as stream:
            yaml.dump(
                config_data,
                stream,
                indent=2,
                default_flow_style=False,
            )

    def _build_repo_objects(self, repos_config):
        repos = []

        for repo_data in repos_config["repos"]:
            repo = SubGitRepo(repo_data)
            repos.append(repo)

        return repos

    def repo_status(self):
        self._resolve_recursive_config_path()
        config = self._get_config_file()
        repos = self._build_repo_objects(config)

        if len(repos) == 0:
            log.critical("  No data for repositories found in config file")
            return 1

        for repo in repos:
            log.info("")
            log.info(f"{repo.name}")
            log.info(f"  {repo.url}")
            log.info(f"  {repo.repo_root().resolve()}")
            log.info(f"  Is cloned to disk? {bool_to_str(repo.is_cloned_to_disk)}")

            if repo.is_cloned_to_disk:
                fetch_file_path = repo.git_fetch_head_file_path

                if fetch_file_path.exists():
                    output, stderr = run_cmd(f"stat -c %y {fetch_file_path}")
                    parsed_output = str(output).replace('\\n', '')

                    log.info(f"  Last pull/fetch: {parsed_output}")
                else:
                    log.info("  Last pull/fetch: Repo has not been pulled or fetch since initial clone")
            else:
                log.info("  Last pull/fetch: UNKNOWN repo not cloned to disk")

            log.info(f"  Repo is dirty? {bool_to_str(repo.is_git_repo_dirty)}")
            log.info(f"  Revision:")

            if repo.revision_type == REVISION_BRANCH:
                log.info(f"    branch: {repo.revision_value}")

                if repo.is_cloned_to_disk:
                    if repo.revision_value in repo.git_repo.heads:
                        git_commit = repo.git_repo.heads[repo.revision_value].commit

                        commit_hash = str(git_commit)
                        commit_message = str(git_commit.summary)
                        has_newer_commit = repo.git_repo.remotes.origin.refs["master"].commit != git_commit
                        is_in_origin = f"{repo.revision_value in repo.git_repo.remotes.origin.refs}"
                    else:
                        commit_hash = "Local branch not found"
                        commit_message = "Local branch not found"
                        has_newer_commit = "---"
                        is_in_origin = "Local branch not found"
                else:
                    commit_hash = "Repo not cloned to disk"
                    commit_message = "Repo not cloned to disk"
                    has_newer_commit = "Repo not cloned to disk"
                    is_in_origin = "Repo not cloned to disk"

                log.info(f"      commit hash: {commit_hash}")
                log.info(f"      commit message: '{commit_message}'")
                log.info(f"      branch exists in origin? {is_in_origin}")
                log.info(f"      has newer commit in origin? {has_newer_commit}")

            if repo.revision_type == REVISION_COMMIT:
                log.info("     FIXME: Not implemented yet")
                log.info(f"    commit: {repo.revision_value}")

            if repo.revision_type == REVISION_TAG:
                log.info(f"    tag: {repo.revision_value}")

                if repo.is_cloned_to_disk:
                    if repo.revision_value in repo.git_repo.tags:
                        tags_commit = repo.git_repo.tags[repo.revision_value].commit
                        commit_hash = str(tags_commit)
                        commit_summary = str(tags_commit.summary)
                    else:
                        commit_hash = "Tag not found"
                        commit_summary = "---"
                else:
                    commit_hash = "Repo not cloned to disk"
                    commit_summary = "Repo not cloned to disk"

                log.info(f"      commit hash: {commit_hash}")
                log.info(f"      commit message: {commit_summary}")

    def yes_no(self, question):
        log.info(question)

        if self.answer_yes:
            log.info("--yes flag set, automatically answer yes to question")
            return True

        answer = input("(y/n) << ")

        return answer.lower().startswith("y")

    def fetch(self, repos_to_fetch):
        """
        Runs "git fetch" on one or more git repos

        To fetch all enabled repos send in None as value

        To fetch a subset of repo names, send in them as a list of strings

        A empty list of items will not fetch any repo
        """
        log.debug(f"Repo names fetch input - {repos_to_fetch}")
        
        self._resolve_recursive_config_path()
        config = self._get_config_file()
        repos = self._build_repo_objects(config)

        if isinstance(repos_to_fetch, list):
            # If we provide a list of repos we need to filter them out from all repo objects
            repos = list(filter(lambda obj: obj.name in repos_to_fetch, repos))

        log.info(f"Git repos to fetch: {repos}")

        if len(repos) == 0:
            # TODO: Convert to an exception
            log.critical("No repos found to filter out. Check config file and cli arguments")
            return 1

        missing_any_repo = False

        for repo in repos:
            if not repo.is_cloned_to_disk:
                log.error(f"Repo {repo.name} not found on disk. You must pull to do a initial clone before fetching can be done")
                missing_any_repo = True

        if missing_any_repo:
            # TODO: Convert to an exception
            return 1

        with Pool(WORKER_COUNT) as pool:
            pool.map(self._fetch_repo, repos)

        log.info("Fetch command run on all git repos completed")
        return 0

    def _fetch_repo(self, repo):
        log.info(f"Fetching git repo '{repo.name}'")
        fetch_results = repo.fetch_repo()
        log.info(f"Fetching completed for repo '{repo.name}'")

        for fetch_result in fetch_results:
            log.info(f" - Fetch result: {fetch_result.name}")

    def pull(self, repos_to_pull):
        """
        To pull all repos defined in the configuration send in repos_to_pull=None

        To pull a subset of repos send in a list of strings repos_to_pull=["repo1", "repo2"]
        """
        log.debug(f"Repo pull - {repos_to_pull}")

        self._resolve_recursive_config_path()
        config = self._get_config_file()
        repos = self._build_repo_objects(config)

        # Filter out any repo object that is not enabled
        repos = list(filter(lambda obj: obj.is_enabled is True, repos))

        if len(repos) == 0:
            # TODO: Convert to an exception
            log.error("There is no repos defined or enabled in the config")
            return 1

        if repos_to_pull is None:
            repo_choices = ", ".join([repo.name for repo in repos])
            answer = self.yes_no(f"Are you sure you want to 'git pull' the following repos '{repo_choices}'")

            if answer is False:
                # TODO: Convert to an exception
                log.warning("User aborted pull step")
                return 1
        elif isinstance(repos_to_pull, list):
            # Validate that all names we have sent in really exists in the config
            is_all_repos_valid = all([repo.name in repos_to_pull for repo in repos])

            # If we send in a list of a subset of repos we want to pull, filter out the repos
            # that do not match these names
            repos = list(filter(lambda obj: obj.name in repos_to_pull, repos))
        else:
            log.debug(f"Names {repos_to_pull}")
            raise SubGitConfigException("Unsuported value type for argument names")

        if not repos:
            raise SubGitConfigException("No valid repositories found")

        # Validation step across all repos to manipulate that they are not dirty
        # or anything uncommited that would break the code trees.
        #
        # Abort out if any repo is bad.

        has_dirty = False

        for repo in repos:
            # If the path do not exists then the repo can't be dirty
            if not repo.repo_root().exists():
                continue

            # A dirty repo means there is uncommited changes in the tree
            if repo.git_repo.is_dirty():
                log.error(f'The repo "{repo.name}" is dirty and has uncommited changes in the following files')
                dirty_files = [
                    item.a_path
                    for item in repo.git_repo.index.diff(None)
                ]

                for file in dirty_files:
                    log.info(f" - {file}")

                has_dirty = True

        if has_dirty:
            # TODO: Convert to an exception
            log.error("Found one or more dirty repos. Resolve it before continue...")
            return 1

        # Repos looks good to be pulled. Run the pull logic for each repo in sequence
        for repo in repos:
            log.info("")

            # Boolean value wether repo is newly cloned.
            cloned = False

            if not repo.is_cloned_to_disk:
                cloned = True

                try:
                    # Cloning a repo w/o a specific commit/branch/tag it will clone out whatever default
                    # branch or where the origin HEAD is pointing to. After we clone we can then move our
                    # repo to the correct revision we want.
                    repo.clone_repo()
                    log.info(f'Successfully cloned repo "{repo.name}" from remote server')
                except Exception as e:
                    raise SubGitException(f'Clone "{repo.name}" failed') from e

            log.debug("TODO: Parse for any changes...")
            # TODO: Check that origin remote exists

            # Fetch all changes from upstream git repo
            repo.fetch_repo()
            revision = repo.revision_value

            # How to handle the repo when a branch is specified
            if repo.revision_type == REVISION_BRANCH:
                log.debug("Handling branch pull case")

                if not cloned:
                    try:
                        latest_remote_sha = str(repo.git_repo.rev_parse(f"origin/{revision}"))
                        latest_local_sha = str(repo.git_repo.head.commit.hexsha)

                        if latest_remote_sha != latest_local_sha:
                            repo.remotes.origin.pull()
                    except git.exc.BadName as er:
                        log.error(er)

                # Ensure the local version of the branch exists and points to the origin ref for that branch
                repo.git_repo.create_head(f"{revision}", f"origin/{revision}")

                # Checkout the selected revision
                # TODO: This only support branches for now
                repo.git_repo.heads[revision].checkout()

                log.info(f'Successfully pull repo "{repo.name}" to latest commit on branch "{repo.revision_value}"')
                log.info(f"Current git hash on HEAD: {str(repo.git_repo.head.commit)}")
            elif repo.revision_type == REVISION_TAG:
                #
                # Parse and extract out all relevant config options and determine if they are nested
                # dicts or single values. The values will later be used as input into each operation.
                #
                tag_config = repo.revision_value

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
                        raise SubGitConfigException("filter option must be a list of items or a single string")

                    order_config = tag_config.get("order", None)

                    if order_config is None:
                        order_algorithm = OrderAlgorithms.SEMVER
                    else:
                        order_algorithm = OrderAlgorithms.__members__.get(order_config.upper(), None)

                        if order_algorithm is None:
                            raise SubGitConfigException(f"Unsupported order algorithm chose: {order_config.upper()}")

                    select_config = tag_config.get("select", None)
                    select_method = None

                    if select_config is None:
                        raise SubGitConfigException("select key is required in all tag revisions")

                    log.debug(f"select_config: {select_config}")

                    # We have sub options to extract out
                    if isinstance(select_config, dict):
                        select_method_value = select_config["method"]
                        select_config = select_config["value"]

                        log.debug(f"select_method: {select_method_value}")

                        select_method = SelectionMethods.__members__.get(select_method_value.upper(), None)

                        if select_method is None:
                            raise SubGitConfigException(f"Unsupported select method chosen: {select_method_value.upper()}")
                    else:
                        # By default we should treat the select value as a semver string
                        select_method = SelectionMethods.SEMVER
                else:
                    raise SubGitConfigException(f"Key revision.tag for repo {repo.name} must be a string or dict object")

                log.debug(f"{filter_config}")
                log.debug(f"{order_config}")
                log.debug(f"{order_algorithm}")
                log.debug(f"{select_config}")
                log.debug(f"{select_method}")

                # Main tag parsing logic

                git_repo_tags = list(repo.git_repo.tags)
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
                    raise SubGitRepoException("No git tag could be parsed out with the current repo configuration")

                log.info(f"Attempting to checkout tag '{select_output}' for repo '{repo.name}'")

                # Otherwise atempt to checkout whatever we found. If our selection is still not something valid
                # inside the git repo, we will get sub exceptions raised by git module.
                repo.git.checkout(select_output)

                log.info(f"Checked out tag '{select_output}' for repo '{repo.name}'")
                log.info(f"Current git hash on HEAD: {str(repo.git_repo.head.commit)}")
                log.info(f"Current commit summary on HEAD in git repo '{repo.name}': ")
                log.info(f"  {str(repo.git_repo.head.commit.summary)}")

            # Handle sparse checkout by configure the repo
            if repo.sparse_checkout_enabled:
                log.info(f"Enable sparse checkout on repo {repo.name}")

                # Always ensure that sparse is enabled
                repo.git.sparse_checkout("init")

                repos = [
                    str(path)
                    for path in repo.sparse_checkout_config["paths"]
                ]

                # Set what paths we defined to be checked out
                repo.git.sparse_checkout("set", *repos)

                # List all items (files and directories) in the cwd
                items = list(repo.repo_root().iterdir())

                # Filter out the '.git' folder
                visible_items = [
                    item
                    for item in items
                    if item.name != '.git'
                ]

                log.debug(f"Visible items after filtering {visible_items}")

                if len(visible_items) == 0:
                    log.warning("You have sparse checkout enabled but no files was found in the git repo after your filter. Possible that your paths do not match any content in the git repo.")
            else:
                # By always setting disable as a default, this will automatically revert any repo
                # that used to have sparse enabled but no longer is ensabled
                log.debug(f"Disabling sparse checkout on repo {repo.name}")
                repo.git.sparse_checkout("disable")

    def _filter_for_selected_repos(self, repos, filter_list):
        if not filter_list:
            return repos

        return list(filter(lambda repo: repo.name in filter_list, repos))

    def delete(self, repo_names=None):
        """
        Helper method that recieves a list of repos. Deletes them as long as not one or
        more of them creates a conflict. (e.g repo(s) is not in the config file,
        path(s) is not to a valid git repo or repo(s) is dirty)
        """
        self._resolve_recursive_config_path()
        config = self._get_config_file()
        repos = self._build_repo_objects(config)
        repos = self._filter_for_selected_repos(repos, repo_names)

        has_dirty_repos = False
        good_repos = []

        if not repos:
            log.critical(f"No git repos to delete selected")
            return 1

        repo_choices = ", ".join([
            repo.name
            for repo in repos
        ])

        answer = self.yes_no(f"Are you sure you want to delete the following repos '{repo_choices}'?")

        if answer:
            for repo in repos:
                if not repo.is_cloned_to_disk:
                    # This repo is already not present or cloned on disk, continue to next repo
                    log.info(f"Git repo '{repo.name}' is already deleted on disk")
                    continue

                if self._check_remote(repo.git_repo):
                    # If repo is dirty, or uncommited changes, the folder can't be removed until that is fixed
                    log.critical(f"'{repo.name}' has some diff(s) in the local repo or the remote that needs be taken care of before deletion")
                else:
                    # If repo is clean then we try to delete it
                    shutil.rmtree(repo.repo_root().resolve())
                    log.info(f"Successfully removed folder: {repo.repo_root()} for repo '{repo.name}'")

    def reset(self, repo_names=None, hard_flag=None):
        """
        Will take a list of repos and find any diffs and reset them back
        to the same state they were when they were first pulled.
        """
        self._resolve_recursive_config_path()
        config = self._get_config_file()
        repos = self._build_repo_objects(config)
        repos = self._filter_for_selected_repos(repos, repo_names)
        # TODO: Add back filtering out of inactive repos

        dirty_repos = []

        if not repos:
            log.critical(f"No git repos to delete selected")
            return

        repo_choices = ", ".join([
            repo.name
            for repo in repos
        ])

        answer = self.yes_no(f"Are you sure you want to reset the following repos '{repo_choices}'?")

        if answer:
            for repo in repos:
                if not repo.is_cloned_to_disk:
                    # This repo is already not present or cloned on disk, continue to next repo
                    log.info(f" - Unable to reset git repo '{repo.name}', it is not cloned to disk. Pull the repo first")
                    continue

                if self._check_remote(repo.git_repo):
                    dirty_repos.append(repo)
                else:
                    log.info(f" - {repo.name} is clean, nothing to reset")

            if not dirty_repos:
                log.error("No repos found to reset. Exiting...")
                return 1

            # Resets repo back to the latest remote commit.
            # If the repo has untracked files, it will not be removed unless '--hard' flag is specified.
            for repo in dirty_repos:
                flag = "--hard" if hard_flag else None
                repo.git.reset(flag)
                log.info(f" - Successfully reset {repo.name}")

    def clean(self, repo_names=None, recurse_into_dir=None, force=None, dry_run=None):
        """
        Method to look through a list of repos and remove untracked files
        """
        self._resolve_recursive_config_path()
        config = self._get_config_file()
        repos = self._build_repo_objects(config)
        repos = self._filter_for_selected_repos(repos, repo_names)
        # TODO: Add back filtering out of inactive repos

        dirty_repos = []
        recursive_flag = "d" if recurse_into_dir else ""
        force_flag = "f" if force else ""
        dry_run_flag = "n" if dry_run else ""
        flags = f"-{recursive_flag}{force_flag}{dry_run_flag}"

        if not repos:
            log.error(f"No git repos to clean selected")
            return

        for repo in repos:
            if not repo.is_cloned_to_disk:
                log.warning(f" - Git repo '{repo.name}' is not cloned to disk. Skipping")
                continue

            if self._check_remote(repo.git_repo):
                log.info(f" - Dirty Git repo '{repo.name}' found, adding to clean list")
                dirty_repos.append(repo)
            else:
                log.info(f" - Git repo '{repo.name}' is not dirty, nothing to clean")

        if not dirty_repos:
            log.error(" - No dirty git repos found to clean")
            return

        for dirty_repo in dirty_repos:
            try:
                clean_return = dirty_repo.git.clean(flags)

                log.info(f"   Clean Repo output: {repo.name}")
                log.info(f"   '{clean_return}'")
            except git.exc.GitCommandError as er:
                log.critical(er)
                return

        if not dry_run:
            log.info("Successfully cleaned repo(s)")
        else:
            log.info("Command was a dry run. No changes has been saved")

    def _check_remote(self, repo):
        """
        Takes repo object and name of directory to check. Returns True if repo has either
        differences in remote and local commits, and/or has any untracked files.
        """
        has_remote_difference = False

        for remote in repo.remotes:
            for branch in repo.branches:
                try:
                    remote_commit = remote.refs[str(branch)].commit
                    local_commit = repo.heads[str(branch)].commit
                except IndexError:
                    has_remote_difference = True

                if (remote_commit != local_commit) or repo.is_dirty(untracked_files=True):
                    has_remote_difference = True

        return has_remote_difference

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

        log.debug("Running clean step on data")

        if not isinstance(regex_list, list):
            raise SubGitConfigException("sequence for clean step must be a list of items")

        if not isinstance(regex_list, list):
            raise SubGitConfigException("regex_list for clean step must be a list of items")

        # If we have no regex to filter against, then return original list unaltered
        if len(regex_list) == 0:
            return sequence

        for item in sequence:
            for filter_regex in regex_list:
                if not isinstance(filter_regex, str):
                    raise SubGitConfigException("ERROR: filter regex must be a string")

                # A empty regex string is not valid
                if filter_regex.strip() == "":
                    raise SubGitConfigException("ERROR: Empty regex filter string is not allowed")

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

        If unsupported order_method is specified, it will thro SubGitConfigException

        Returns a new list with the sorted sequence of items
        """
        ordered_sequence = []

        if order_method == OrderAlgorithms.SEMVER:
            log.debug("Ordering sequence of items by PEP440 SEMVER logic")
            log.debug(sequence)

            # By using packages module and Version class we can properly compare semver
            # versions with PEP440 compatible version compare
            ordered_sequence = list(sorted(sequence, key=lambda x: version.Version(str(x))))
        elif order_method == OrderAlgorithms.TIME:
            log.debug("Ordering sequence of items by TIME they was created, input:")
            log.debug(sequence)

            # When sorting by time the latest item in the sequence with the highest or most recent time
            # will be on index[0] in the returned sequence
            ordered_sequence = list(sorted(sequence, key=lambda t: t[1]))
        elif order_method == OrderAlgorithms.ALPHABETICAL:
            log.debug("Order sequence of items by ALPHABETICAL string order")
            log.debug(sequence)

            # By default sorted will do alphabetical sort
            ordered_sequence = list(sorted(sequence))
        else:
            raise SubGitConfigException("Unsupported ordering algorithm selected")

        log.debug(f"Ordered sequence result: {ordered_sequence}")

        return ordered_sequence

    def _select(self, sequence, selection_query, selection_method):
        """
        Given a sequence of objects, perform the selection based on the selection_method and the
        logic that it implements.

        Supported selection methods: SEMVER, EXACT

        If unsupported selection_method is specified, it will throw SubGitConfigException

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
                log.debug("Selection query")

                try:
                    spec = SpecifierSet(selection_query)

                    filtered_versions = list(
                        spec.filter([str(item) for item in sequence]),
                    )

                    log.debug("filtered_versions")
                    log.debug(filtered_versions)

                    return filtered_versions[-1]
                except packaging.specifiers.InvalidSpecifier:
                    log.warning("WARNING: Invalid SEMVER select query. Falling back to EXCAT matching of value")
                    selection_method = SelectionMethods.EXACT

        if selection_method == SelectionMethods.EXACT:
            for item in sequence:
                if str(item) == selection_query:
                    return item

            # Query not found in sequence, return None
            return None

        if selection_method not in SelectionMethods.__members__:
            raise SubGitConfigException("Unsupported select algorithm selected")
