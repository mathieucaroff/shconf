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
argument(
    "-u", "--user", help="""\
The name of the user to be used to dermine which files should be sourced, and \
to set the `sc_user` variable."""
)

args = parser.parse_args()

env = getenv.Env()
try:
    getenv.getenv(
        env=env,
        user=args.user,
        sh=args.shell,
    )
    sys.stdout.write(env.setenv)
except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    import traceback
    traceback.print_exception(
        exc_type, exc_value, exc_traceback,
        limit=2,
        file=sys.stderr,
    )

sourcing = sourcing.sourcing(
    env=env,
    directoryList=args.directory,
)
sys.stdout.write(sourcing)
