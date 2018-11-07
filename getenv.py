class Env:
    __slots__ = "root os pm dist sh host isRemote isRoot isSudo".split()
    __slots__.extend("setenv".split())

    def propertyList(self, pnameList=None):
        if pnameList is None:
            pnameList = Env.__slots__
        return tuple(
            getattr(self, propname) for propname in pnameList
        )


def getenv(sh=None):
    import re
    import os as os
    import socket
    import sys

    def getos():
        return {
            "linux2": "linux",
            "linux3": "linux",
            "win32": "windows"
        }.get(sys.platform, sys.platform)
        # return re.match("[a-zA-Z]+", sys.platform)

    def getdist():
        try:
            with open("/etc/os-release") as f:
                for l in f:
                    m = re.match(r"^ID=(.*)$", l)
                    if m:
                        return m.group(1)
        except IOError:
            with open("/etc/system-release") as f:
                l = f.read()
                return l.split()[0]

    def getppid(pid):
        with open("/proc/%d/stat" % pid) as f:
            return int(f.read().split()[6])

    def getpname(pid):
        with open("/proc/%d/comm" % pid) as f:
            return f.read().strip()

    def getsh(ppname):
        return re.sub("^-", "", ppname)

    def getissudo():
        import pwd
        user = pwd.getpwuid(os.getuid()).pw_name
        try:
            with open("/etc/group") as f:
                for l in f:
                    m = re.match(r"^sudo:.?:\d*:(.*)\n", l)
                    if m:
                        return bool(re.search(r"(^|,)%s(,|$)" % user, m.group(1)))
        except IOError:
            pass
        return False

    ekeys = os.environ.keys()
    ppname = getpname(os.getppid())

    e = Env()

    e.root = os.path.dirname(__file__)

    e.os = getos().lower()
    e.pm = None
    e.dist = getdist().lower()
    e.sh = (sh or getsh(ppname)).lower()
    e.host = socket.gethostname().lower()
    e.isRemote = "remote" if (
        "SSH_CLIENT" in ekeys or
        "SSH_TTY" in ekeys or
        "SSH_CONNECTION" in ekeys or
        ppname == "sshd"
    ) else "local"
    e.isRoot = "root" if (os.geteuid() == 0) else "user"
    e.isSudo = "sudo" if getissudo() else "nosudo"

    def l(**kwargs):
        for key, val in kwargs.items():
            return "sc_%s='%s'\n" % (key, val)

    e.setenv = "".join((
        l(root=e.root),
        l(os=e.os),
        l(dist=e.dist),
        l(sh=e.sh),
        l(host=e.host),
        l(is_remote=e.isRemote),
        l(is_root=e.isRoot),
        l(is_sudo=e.isSudo)
    ))

    return e