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
    elif cli_args["<command>"] == "pull":
        sub_args = docopt(sub_diffusion_args, argv=argv)
    else:
        extras(True, sgit.__version__, [Option("-h", "--help", 0, True)], base_args)
        sys.exit(1)

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
