import getenv
import sourcing
import sys
import argparse
from os.path import join, dirname

description = """
Determines the system it is running on, walk the specified diretories,
searching for .sh files whose path matches the caracteristics of the
system, and output an eval-able text to set variables to describe the
running environnement and source the files in the walked directories.
"""

parser = argparse.ArgumentParser(description=description)
argument = parser.add_argument

argument(
    "-d", "--directory", required=True, action="append", help="""\
The directory(ies) to walk, in search of matching .sh files."""
)
argument(
    "-s", "--shell", help="""\
The name of the shell which will eval the output. It is also used \
as the 'sc_shell' variable and to match shell files to be sourced."""
)

args = parser.parse_args()

env = getenv.getenv(args.shell)
sys.stdout.write(env.setenv)

sourcing = sourcing.sourcing(
    env=env,
    directoryList=args.directory
)
sys.stdout.write(sourcing)
