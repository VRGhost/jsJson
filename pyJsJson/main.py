import argparse
import os
import sys
import contextlib
import json
import logging

import pyJsJson

logger = logging.getLogger(__name__)


def get_arg_parser():
    parser = argparse.ArgumentParser(description='Render JSON using a JSON template')
    parser.add_argument('input', help='Input JSON to be rendered')
    parser.add_argument(
        '--search-dirs',
        default=(), nargs='*',
        help='Extra directories to be included into the search path'
    )
    parser.add_argument('--output', default='-', help='Output file ("-" for stdout)')
    return parser


def main(args):
    pyJsJson.util.logging.configureCliLogging()
    logger.info('**** STARTED ****')
    args = get_arg_parser().parse_args(args)

    input_fname = os.path.abspath(args.input)
    search_dirs = list(args.search_dirs)
    search_dirs.insert(
        0,
        os.path.dirname(input_fname)
    )

    expand = pyJsJson.expand.JsonExpand(allowed_search_roots=search_dirs)
    expand.loadCommands(pyJsJson.commands.DEFAULT_COMMANDS)
    tree = expand.loadJsonFile(input_fname)

    out = expand.expand(tree)

    with contextlib.ExitStack() as stack:
        if args.output == '-':
            outf = sys.stdout
        else:
            outf = open(args.output, 'w')
            stack.enter_context(outf)  # ensure that the file will be closed

        json.dump(out, outf, indent=4, sort_keys=True)

    return True  # Report success
