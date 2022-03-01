# -*- coding: utf-8 -*-

# python std lib
import logging
import os
import pdb
import sys
import traceback

# 3rd party imports
from docopt import docopt, extras, Option, DocoptExit


base_args = """
Usage:
    subgit <command> [options] [<args> ...]

Commands:
    fetch    Fetch one or all Git repos
    init     Initialize a new subgit repo
    pull     Update one or all Git repos
    status   Show status of each configured repo

Options:
    --help          Show this help message and exit
    --version       Display the version number and exit
"""


sub_fetch_args = """
Usage:
    subgit fetch [<repo> ...] [options]

Options:
    -y, --yes    Answers yes to all questions (use with caution)
    -h, --help   Show this help message and exit
"""


sub_init_args = """
Usage:
    subgit init [<name> <url>] [options]

Options:
    -y, --yes    Answers yes to all questions (use with caution)
    -h, --help   Show this help message and exit
"""


sub_pull_args = """
Usage:
    subgit pull [<repo> ...] [options]

Options:
    <repo>       Name of repo to pull
    -y, --yes    Answers yes to all questions (use with caution)
    -h, --help   Show this help message and exit
"""


sub_status_args = """
Usage:
    subgit status [options]

Options:
    -y, --yes    Answers yes to all questions (use with caution)
    -h, --help   Show this help message and exit
"""


def parse_cli():
    """Parse the CLI arguments and options."""
    import subgit

    try:
        cli_args = docopt(
            base_args,
            options_first=True,
            version=subgit.__version__,
            help=True,
        )
    except DocoptExit:
        extras(
            True,
            subgit.__version__,
            [Option("-h", "--help", 0, True)],
            base_args,
        )

    # Set INFO by default, else DEBUG log level
    subgit.init_logging(5 if "DEBUG" in os.environ else 4)
    log = logging.getLogger(__name__)

    argv = [cli_args["<command>"]] + cli_args["<args>"]

    if cli_args["<command>"] == "fetch":
        sub_args = docopt(sub_fetch_args, argv=argv)
    elif cli_args["<command>"] == "init":
        sub_args = docopt(sub_init_args, argv=argv)
    elif cli_args["<command>"] == "pull":
        sub_args = docopt(sub_pull_args, argv=argv)
    elif cli_args["<command>"] == "status":
        sub_args = docopt(sub_status_args, argv=argv)
    else:
        extras(
            True,
            subgit.__version__,
            [Option("-h", "--help", 0, True)],
            base_args,
        )
        sys.exit(1)

    # In some cases there is no additional sub args of things to extract
    if cli_args["<args>"]:
        sub_args["<sub_command>"] = cli_args["<args>"][0]

    return (cli_args, sub_args)


def run(cli_args, sub_args):
    """
    Execute the CLI
    """
    log = logging.getLogger(__name__)

    retcode = 0

    log.debug(cli_args)
    log.debug(sub_args)

    from subgit.core import SubGit

    core = SubGit(answer_yes=sub_args["--yes"])

    if cli_args["<command>"] == "fetch":
        repos = sub_args["<repo>"]
        repos = repos or None

        retcode = core.fetch(repos)

    if cli_args["<command>"] == "init":
        repo_name = sub_args["<name>"]
        repo_url = sub_args["<url>"]

        retcode = core.init_repo(repo_name, repo_url)

    if cli_args["<command>"] == "pull":
        repos = sub_args["<repo>"]
        repos = repos or None

        retcode = core.pull(repos)

    if cli_args["<command>"] == "status":
        retcode = core.repo_status()

    return retcode


def cli_entrypoint():
    """Used by setup.py to create a cli entrypoint script."""
    try:
        cli_args, sub_args = parse_cli()
        exit_code = run(cli_args, sub_args)
        sys.exit(exit_code)
    except Exception:
        ex_type, ex_value, ex_traceback = sys.exc_info()

        if "DEBUG" in os.environ:
            extype, value, tb = sys.exc_info()
            traceback.print_exc()
            if "PDB" in os.environ:
                pdb.post_mortem(tb)
            raise
        else:
            print(f"Exception type : {ex_type.__name__}")
            print(f"EXCEPTION MESSAGE: {ex_value}")
            print(f"To get more detailed exception set environment variable 'DEBUG=1'")
            print(f"To PDB debug set environment variable 'PDB=1'")
