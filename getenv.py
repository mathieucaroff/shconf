class Env:
    __slots__ = "rootDir os pm dist sh host remote root sudo init".split()
    __slots__.extend("setenv".split())

    def selectPropertyList(self, pnameList):
        return tuple(
            getattr(self, propname) for propname in pnameList
        )
    
    def fullPropertyList(self):
        return self.selectPropertyList(self.__slots__)


def getenv(sh=None):
    import re
    import os
    import socket
    import sys

    def whichFirst(nameList):
        from distutils.spawn import find_executable as which
        os.environ.setdefault("PATH",
            "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        )
        for name in nameList:
            path = which(name)
            if path is not None:
                yield path

    def getos():
        return {
            "linux2": "linux",
            "linux3": "linux",
            "win32": "windows"
        }.get(sys.platform, sys.platform)
        # return re.match("[a-zA-Z]+", sys.platform)

    def getpm():
        from os.path import basename
        return basename(next(whichFirst("apt yum pacman emerge zypper".split()), "other"))

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

    def getsudo():
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
    e.sudo = "sudo" if getsudo() else "nosudo"
    e.init = "noinit" if "sc_init" in os.environ.keys() else "init"

    def gen(export=False, **kwargs):
        if export:
            if e.sh[-3:] == "csh":
                fmt = "setenv sc_{key} '{value}'\n"
            else:
                fmt = "export sc_{key}='{value}'\n"
        else:
            fmt = "sc_{key}='{value}'\n"
        key, value = list(kwargs.items())[0]
        return fmt.format(
            key=key,
            value=value,
        )

    e.setenv = "".join((
        gen(rootDir=e.rootDir),
        gen(os=e.os),
        gen(pm=e.pm),
        gen(dist=e.dist),
        gen(sh=e.sh),
        gen(host=e.host),
        gen(remote=e.remote),
        gen(root=e.root),
        gen(sudo=e.sudo),
        gen(init=e.init, export=True),
    ))

    return e