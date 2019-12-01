# -*- coding: utf-8 -*-

# python std lib
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
    init          Initialize new sgit repo
    repo          Commands to manipulate .sgit.yaml
    pull          Update a sub repo

Options:
    --help          Show this help message and exit
    --version       Display the version number and exit
"""


sub_init_args = """
Usage:
    sgit init [options]

Options:
    -h, --help          Show this help message and exit
"""


sub_repo_args = """
Usage:
    sgit repo list [options]
    sgit repo add [options]
    sgit repo remove <target> [options]
    sgit repo set url <url> [options]
    sgit repo set rev <rev> [options]

Options:
    -h, --help          Show this help message and exit
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

    if cli_args["<command>"] == "init":
        sub_args = docopt(sub_init_args, argv=argv)
    # elif cli_args["<command>"] == "pull":
    #     sub_args = docopt(sub_diffusion_args, argv=argv)
    elif cli_args["<command>"] == "repo":
        sub_args = docopt(sub_repo_args, argv=argv)
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

    from sgit.core import Sgit

    if cli_args['<command>'] == 'init':
        core = Sgit()
        return core.init_repo()
    elif cli_args['<command>'] == 'repo':
        core = Sgit()

        if sub_args['list']:
            core.repo_list()
        elif sub_args['add']:
            core.repo_add()
        elif sub_args['remove']:
            core.repo_remove()
        elif sub_args['set']:
            # TODO: url
            # TODO: rev
            core.repo_set()


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
