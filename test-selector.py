import sys
import sourcing

class Env:
    pass

e = Env()

e.os = "linux"
e.pm = "apt"
e.dist = "ubuntu"
e.sh = "bash"
e.host = "sefidos"
e.isRemote = "local"
e.isRoot = "user"
e.isSudo = "sudo"

selectable = sys.argv[1]

sourcetext = sourcing.sourcing(e, selectable)
sys.stdout.write(sourcetext)