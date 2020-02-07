# -*- coding: utf-8 -*-

# python std lib
import os
import pdb
import re
import sys
import traceback

# sgit imports

# 3rd party imports
from docopt import docopt


base_args = """
Usage:
    sgit <command> [options] [<args> ...]

Available sgit commands are:
    repo          Commands to manipulate .sgit.yaml
    update        Update a sub repo

Options:
    --help          Show this help message and exit
    --version       Display the version number and exit
"""


sub_repo_args = """
Usage:
    sgit repo init [options]
    sgit repo list [options]
    sgit repo add <name> <url> <rev> [options]
    sgit repo remove <name> [options]
    sgit repo set <name> url <url> [options]
    sgit repo set <name> rev <rev> [options]
    sgit repo rename <from> <to> [options]

Options:
    -h, --help          Show this help message and exit
"""


sub_update_args = """
Usage:
    sgit update [<repo>] [options]

Options:
    <repo>      Name of repo to update
    -h, --help  Show this help message and exit
"""


def parse_cli():
    """Parse the CLI arguments and options."""
    import sgit

    from docopt import extras, Option, DocoptExit

    try:
        cli_args = docopt(
            base_args, options_first=True, version=sgit.__version__, help=True
        )
    except DocoptExit:
        extras(True, sgit.__version__, [Option("-h", "--help", 0, True)], base_args)

    argv = [cli_args["<command>"]] + cli_args["<args>"]

    if cli_args["<command>"] == "repo":
        sub_args = docopt(sub_repo_args, argv=argv)
    elif cli_args["<command>"] == "update":
        sub_args = docopt(sub_update_args, argv=argv)
    else:
        extras(True, sgit.__version__, [Option("-h", "--help", 0, True)], base_args)
        sys.exit(1)

    # In some cases there is no additional sub args of things to extract
    if cli_args['<args>']:
        sub_args["<sub_command>"] = cli_args["<args>"][0]

    return (cli_args, sub_args)

def run(cli_args, sub_args):
    """Execute the CLI."""
    retcode = 0

    if 'DEBUG' in os.environ:
        print(cli_args)
        print(sub_args)

    from sgit.core import Sgit

    if cli_args['<command>'] == 'repo':
        core = Sgit()

        if sub_args['init']:
            retcode = core.init_repo()
        elif sub_args['list']:
            retcode = core.repo_list()
        elif sub_args['add']:
            retcode = core.repo_add(
                sub_args['<name>'],
                sub_args['<url>'],
                sub_args['<rev>'],
            )
        elif sub_args['remove']:
            retcode = core.repo_remove(
                sub_args['<name>'],
            )
        elif sub_args['set']:
            url = sub_args['url']
            rev = sub_args['rev']

            if url:
                retcode = core.repo_set(
                    sub_args['<name>'],
                    'url',
                    sub_args['<url>'],
                )
            elif rev:
                retcode = core.repo_set(
                    sub_args['<name>'],
                    'rev',
                    sub_args['<rev>'],
                )
        elif sub_args['rename']:
            from_name = sub_args['<from>']
            to_name = sub_args['<to>']

            retcode = core.repo_rename(
                from_name,
                to_name,
            )

    if cli_args['<command>'] == 'update':
        core = Sgit()

        if sub_args['update']:
            repo = sub_args['<repo>']
            repo = repo if repo else 'all'

            retcode = core.update(repo)

    return retcode


def cli_entrypoint():
    """Used by setup.py to create a cli entrypoint script."""
    try:
        cli_args, sub_args = parse_cli()
        exit_code = run(cli_args, sub_args)
        sys.exit(exit_code)
    except Exception:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)
        raise
