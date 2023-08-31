import git

from git import Git, Repo
from pathlib import Path
from subgit.constants import *
from subgit.exceptions import *


class SubGitRepo(object):

    def __init__(self, repo_config, *args, **kwargs):
        self.raw_config = repo_config
        self.repo_cwd = Path(".")
        self.name = repo_config.get("name", None)
        self.clone_point = Path(".")  # Clone point 
        self.is_enabled = repo_config.get("enable", True)
        self.url = repo_config.get("url", "NOT SET")  # repo url:en som git fattar
        self.revision_type = ""  # branch, tag, commit
        self.revision_value = ""  # namnet på saken
        self.is_cloned_to_disk = None
        self.sparse_checkout_config = repo_config.get("sparse", None)
        self.sparse_checkout_enabled = True if self.sparse_checkout_config else False

        self.refresh_git_repo()

        # TODO: Simplify this to not be as repetetive as now
        repo_branch = repo_config["revision"].get("branch", None)
        repo_commit = repo_config["revision"].get("commit", None)
        repo_tag = repo_config["revision"].get("tag", None)

        if repo_branch:
            self.revision_type = REVISION_BRANCH
            self.revision_value = repo_branch
        if repo_commit:
            self.revision_type = REVISION_COMMIT
            self.revision_value = repo_commit
        if repo_tag:
            self.revision_type = REVISION_TAG

            if isinstance(repo_tag, str):
                self.revision_value = repo_tag
            elif isinstance(repo_tag, dict):
                self.revision_value = repo_tag["select"]

                # If value is nested inside a dict explicit
                if isinstance(self.revision_value, dict):
                    self.revision_value = repo_tag["select"]["value"]

    def clone_repo(self):
        """
        Helper action that will clone the configured git repo based on the url
        and the root folder path
        """
        if not self.url:
            raise SubGitConfigException(f"Missing required key 'url' on repo '{self.name}'")

        Repo.clone_from(
            self.url,
            self.repo_root(),
        )

        self.refresh_git_repo()

    def fetch_repo(self):
        return self.git_repo.remotes.origin.fetch()

    def refresh_git_repo(self):
        """
        Helper method that is supposed to recreate the Repo and Git objects
        """
        try:
            self.git_repo = Repo(self.repo_root())
            self.git = Git(self.repo_root())

            # If we do not get any exception, then we assume that folder and git
            # repo exists locally on our machine
            self.is_cloned_to_disk = True
        except git.exc.NoSuchPathError:
            self.is_cloned_to_disk = False

    @property
    def git_fetch_head_file_path(self):
        """
        Dynamically calculate this repo path each time
        """
        return self.repo_root() / ".git/FETCH_HEAD"

    def is_git_repo_dirty(self):
        return self.git_repo.is_dirty()

    def is_git_repo_dirty_str(self):
        return "Yes" if self.is_git_repo_dirty else "No"

    def is_cloned_to_disk_str(self):
        return "Yes" if self.is_cloned_to_disk else "No"

    def repo_root(self):
        """
        Combines repo_cwd + clone_point into the root folder that
        the repo should be cloned to
        """
        return self.repo_cwd / self.name / self.clone_point

    def print_status(self):
        pass

    def to_dict(self):
        """
        Compiles and returns the object as a dict. This is not the same as the raw config
        values that was set from repo_config but all the calculated values after initialization
        """
        return vars(self)

    def __repr__(self):
        return f"SubGitRepo - {self.name} - {self.repo_root().resolve()} - {self.url} - {self.revision_type}/{self.revision_value}"
