import getenv
import sourcing
import sys
from os.path import join


# assert len(sys.argv) >= 1, "You must provide the name of the shell."
sh = None
if len(sys.argv) > 1:
    sh = sys.argv[1]

env = getenv.getenv(sh)

sys.stdout.write(env.setenv)

sourcing = sourcing.sourcing(
    env=env,
    selectable=join(env.root, "selectable")
)

sys.stdout.write(sourcing)