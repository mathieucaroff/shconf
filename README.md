# shconf

A librairy to help source the right rc files on each device.

Version 0.0.1

CC0 License

## Install

```bash
git clone https://github.com/mathieucaroff/shconf.git ~/.sc
mkdir -p ~/.sc/selectable/rc_sh.d

# bash
mv ~/.bashrc ~/.sc/selectable/rc_sh.d/bashrc_bash.sh
echo '<(python ~/.sc/shconf.py bash)' >> ~/.bashrc

# zsh
mv ~/.zshrc ~/.sc/selectable/rc_sh.d/zshrc_zsh.sh
echo '<(python ~/.sc/shconf.py zsh)' >> ~/.zshrc

# you can install both, it's what shconf was made for
```

## Feature

`shconf` fundamentaly does two things:

* It provides 8 variables about the device you are running on and the session.
  You can use those variables in your shell
* It sources the filess in `selectable/` according to those variable values.

## The 8 variables

```bash
sc_os='linux' # or 'darwin' or 'freebsd' ...
sc_pm='apt' # or 'yum' or 'pacman' or 'emerge' or 'zypper'
sc_dist='ubuntu' # or 'debian' or 'fedora' or 'centos' or 'gentoo'
sc_sh='bash' # or 'zsh' or 'dash' or 'fish' or 'xonsh' or 'ionsh'
sc_host='output of `hostname`'
sc_remote='local' # either 'local' or 'remote'
sc_root='user' # either 'user' or 'root'
sc_sudo='sudo' # either 'sudo' or 'nosudo'
```

The `sc_sudo` variable tells whether the current user is part of the sudo group.

Note:
Most of these values are obtained in python by reading files and rather than by
running commands.

### Other variables

sc_root_dir='/mnt/c/Dropbox/code/oxshconf'

## The sourcing rules

Once shconf has gather all the relevant informations, it start walking
`selectable/` to determine which files in it respect the naming convention.

A directory respects the naming convention if and only if its name finishes in
`.d` and it is in a directory which respect the naming convention, with the
following exception: `selectable/` itself, respect the naming convention.

A file respect the naming convention if and only if it is in a directory which
respect the naming convention and its name finishes in `.sh`

### The pattern matching rules

The `_` is a special character. It is the criterion perfix in directory names,
as well as the match value prefix in file names. In a filename, the criterion or
match value spans form the character `_` to one of:

* the next character `_` (which must me announcing another criterion / value)
* the final `.` of `.d` or of `.sh`.

A criterion (in directory names), is one of the 8 variable names, without `sc_`.

A match value (in a file name), is one of:

* A single accepted value for the variable corresponding to the criterion.
  For instance `bash` for the criterion `sh` or `linux` for `os`.
* A comma-separated list of accepted values for the criterion variable.
  For instance `dash,bash,zsh` for `sh` or `apt,yum` for `pm`.
* An empty value ``. This will match any value of teh crieterion variable.
* The special value "unknown" `~`. This matches any value contained in no other
  matching value of the directory `selectable/` for that criterion.

Note: the matching value `bzsh` is special and expands to `bzsh,bash,zsh`.
`bzsh` is preserved in the expansion result to allow matching the hostname
`bzsh`. This expansion is rather handy given that bash and zsh are almost the
same and thus will read many configuration files in the same way.

There can be zero, one or several criteria in one directory name. If there are
several directories with criterion(a) in the path of a file, they are
concatenated. No directory path may contain twice the same criterion, or it
won't be walked and a message will be issued on stderr.

There must be as many matching values in a file basename as there are criteria
in the path which comes before it. Futhermore, the order of the criteria in the
path and of the matching values in the filename must match, with one exception:

* If there are no criterion in the directory path of a file, but there are
  matching values in it's name, the matching values will be matched against any
  of the available criterion values.
  In the case of that exception, the matching value `~` cannot be used in the
  filename because it's behavior would be to the least ambigous. shconf will
  refuse to execute such a file and prompt the user to remove that maching
  value.

## Examples

Let's suppose your current environement is:

```bash
sc_os='linux'
sc_pm='apt'
sc_dist='ubuntu'
sc_sh='bash'
sc_host='sefidos'
sc_remote='local'
sc_root='user'
sc_sudo='sudo'
```

The following files will be matched:

```txt
selectable/perShell_sh.d/alias_bash.sh
selectable/perShell_sh.d/alias_bzsh.sh
selectable/perShell_sh.d/alias_bach,dash.sh
selectable/perShell_sh.d/alias_.sh

# Criterionless matching:
selectable/alias.d/_bash.sh
```

The following files won't be matched:

```txt
selectable/perShell_sh.d/alias_zsh.sh
```

The following path are badly constructed and cannot be matched in any situation:

```txt
selectable
```