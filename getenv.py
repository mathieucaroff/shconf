class Env:
    __slots__ = "rootDir os pm dist sh host remote root sudo".split()
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

    def whichFirst(nameList, default):
        from distutils.spawn import find_executable as which
        for x in map(which, nameList):
            if x is not None:
                yield x
        yield default

    def getos():
        return {
            "linux2": "linux",
            "linux3": "linux",
            "win32": "windows"
        }.get(sys.platform, sys.platform)
        # return re.match("[a-zA-Z]+", sys.platform)

    def getpm():
        from os.path import split
        return split(next(whichFirst("apt yum pacman emerge zypper".split(), "other")))[-1]

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
        name = re.sub("^-", "", ppname)
        if name == "sh":
            name = "dash"
        return name

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

    e.rootDir = os.path.dirname(__file__)

    e.os = getos().lower()
    e.pm = getpm()
    e.dist = getdist().lower()
    e.sh = (sh or getsh(ppname)).lower()
    e.host = socket.gethostname().lower()
    e.remote = "remote" if (
        "SSH_CLIENT" in ekeys or
        "SSH_TTY" in ekeys or
        "SSH_CONNECTION" in ekeys or
        ppname == "sshd"
    ) else "local"
    e.root = "root" if (os.geteuid() == 0) else "user"
    e.sudo = "sudo" if getissudo() else "nosudo"

    def l(**kwargs):
        for key, val in kwargs.items():
            return "sc_%s='%s'\n" % (key, val)

    e.setenv = "".join((
        l(rootDir=e.rootDir),
        l(os=e.os),
        l(pm=e.pm),
        l(dist=e.dist),
        l(sh=e.sh),
        l(host=e.host),
        l(remote=e.remote),
        l(root=e.root),
        l(sudo=e.sudo)
    ))

    return e