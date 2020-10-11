import sys
import sourcing
import getenv

class Env(getenv.Env):
    pass

e = Env()

e.rootDir = ""
e.setenv = ""

e.os = "linux"
e.pm = "apt"
e.dist = "ubuntu"
e.sh = "bash"
e.host = "sefidos"
e.remote = "local"
e.root = "user"
e.sudo = "sudo"
e.init = "init"
e.user = "ox"

selectable = sys.argv[1]

sourcetext = sourcing.sourcing(e, selectable)
sys.stdout.write(sourcetext)