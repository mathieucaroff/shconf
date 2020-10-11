from pprint import pprint
import sys
import re
from collections import namedtuple

PATTERN_SLOT_SEPARATOR = "_"
PATTERN_ALTERNATIVE_SEPARATOR = ","
SH_FILE_REGEX = r'^([^_]*)?((_[^_]*)*)\.sh$'
SH_DIR_REGEX  = r'^([^_]*)?((_[^_]*)*)\.d$'.replace(
    "_",
    PATTERN_SLOT_SEPARATOR
)
PATTERN_ANY_VALUE = ""
PATTERN_OTHER_VALUE = "~"

EXPAND_ALTERNATIVE = {
    "zbash": "zsh bash".split(),
    "dbash": "dash bash".split(),
    "zdbash": "zsh dash bash".split(),
}

callId = 0

def logging(f):
    def wrap(*args, **kwargs):
        global callId
        c = callId
        callId += 1
        print("/\\%s%s%s:" % (f.__name__, c, str(args)))
        # print("kwargs(%s):" % c)
        # print(kwargs)
        ret = f(*args, **kwargs)
        print("\\/%s%s" % (f.__name__, c))
        # pprint(ret)
        return ret
    return wrap

def splitPattern(pattern):
    longSlotList = pattern.split(PATTERN_SLOT_SEPARATOR)
    assert longSlotList[0] == "", "Internal bug '%s' != ''" % longSlotList[0]
    slotList = longSlotList[1:]
    return slotList


def critify(slot):
    """ Change kebab-case into camelCase """
    partList = slot.split("-")
    for i, part in enumerate(partList[1:], 1):
        if len(part) == 0:
            partList[i] = ""
        else:
            partList[i] = part[0].upper() + part[1:]
    crit = "".join(partList)
    return crit


def addCriteria(env, slotList, ff, criteria):
    """Make crit from slot, return an extended criteria list after checkings"""
    newCriteria = criteria[:]
    for slot in slotList:
        crit = critify(slot)
        if (crit in criteria):
            msg = "The criterion `{}` appears twice in the chain `{}`\n"
            sys.stderr.write(msg.format(crit, ff))
        elif (crit not in env.criterionList):
            msg = "The criterion `{}`, in your directory `{}` is invalid\n"
            sys.stderr.write(msg.format(crit, ff))
        else:
            newCriteria.append(crit)
            continue
        raise ValueError("Bad criterion")
    return newCriteria


def checkMakeWellNamedEntry(f, ff, criteria):
    m = re.match(SH_FILE_REGEX, f)
    if m:
        slotList = splitPattern(m.group(2))
        if len(slotList) == len(criteria) or criteria == []:
            wellNamedEntry = WellNamed(ff, slotList, criteria)
            return wellNamedEntry

WellNamed = namedtuple("WellNamed", "filepath slotList criteria")

def walk(env, dirpath, criteria):
    """
    Walk all well-formed directory to establish a list of files which
    respect the naming convention (a "well named" file).
    Return a list of namedtuples("filepath criteria").
    """
    from os import listdir
    from os.path import isfile, join

    for f in listdir(dirpath):
        ff = join(dirpath, f) # Full path to file F
        if isfile(ff):
            wne = checkMakeWellNamedEntry(f, ff, criteria)
            if wne:
                yield wne
        else:
            m = re.match(SH_DIR_REGEX, f)
            if m:
                slotList = splitPattern(m.group(2))
                try:
                    ff_criteria = addCriteria(env, slotList, ff, criteria)
                except ValueError:
                    continue # i.e. do not walk into that directory.
                #print("willExtend with:\n:ff: %s\n:ff_cr: %s" % (ff, ff_criteria))
                for e in walk(env, ff, ff_criteria):
                    yield e


def alternativeFromSlot(slot):
    alternativeList = slot.split(PATTERN_ALTERNATIVE_SEPARATOR)

    for alt in alternativeList:
        if alt in EXPAND_ALTERNATIVE:
            alternativeList.extend(EXPAND_ALTERNATIVE[alt])
        yield alt


def index(wellNamedList):
    propertyIndex = {}
    for filepath, slotList, criteria in wellNamedList:
        if criteria is not None:
            for crit, slotVal in zip(criteria, slotList):
                for alt in alternativeFromSlot(slotVal):
                    propertyIndex.setdefault(crit, set()).add(alt)
    return propertyIndex


def validate(env, wellNamedEntry, propertyIndex):
    """ Checks whether a pattern matches the environement """

    wne = wellNamedEntry
    criteria = wne.criteria

    # /\ case unbound
    unbound = len(criteria) == 0
    propertyList = unbound and env.fullPropertyList()
    # print("sv: %s" % wne.slotList)
    for slotVal in unbound * wne.slotList:
        if slotVal in (PATTERN_OTHER_VALUE, PATTERN_ANY_VALUE):
            msg = """
Found `%s` in file `%s` but this is useless because there are no corresponding \
criterion. You should remove the string `%s` from the file name. Cautiously not\
sourcing that file.
"""[1:]
            toRemove = PATTERN_SLOT_SEPARATOR + slotVal
            sys.stderr.write(msg % (slotVal, wne.filepath, toRemove))
            return False

        if not any(alt in propertyList for alt in alternativeFromSlot(slotVal)):
            return False
    if unbound:
        return True
    # \/ case unbound


    # /\ case bound
    propertyList = env.selectPropertyList(wne.criteria)
    #print("cr: %s, propertyList: %s" % (str(criteria), str(propertyList)))

    for slotVal, propVal, crit in zip(wne.slotList, propertyList, criteria):
        if slotVal == PATTERN_ANY_VALUE:
            # No matter the corresponding environnment value,
            # we don't need to match anything.
            continue

        if slotVal == PATTERN_OTHER_VALUE:
            knownValSet = propertyIndex[crit]
            if propVal not in knownValSet:
                continue
        if not any(alt == propVal for alt in alternativeFromSlot(slotVal)):
            return False
    return True
    # \/ case bound


def examine(env, wellNamedList, propertyIndex):
    for wellNamedEntry in wellNamedList:
        if validate(env, wellNamedEntry, propertyIndex):
            yield wellNamedEntry.filepath


def sortkey(path):
    from os.path import sep

    partList = path.split(sep)
    numericList = []
    for part in partList:
        num = re.match(r"(\d*)", part).group(1)
        if num:
            numericList.append(num)
    numericList.append(partList[-1])
    return numericList


def sourcing(env, directoryList):
    wellNamedList = [entry for di in directoryList for entry in walk(env, di, [])]
    propertyIndex = index(wellNamedList)
    willSource = list(examine(env, wellNamedList, propertyIndex))
    willSource.sort(key = sortkey)

    sourcePattern = "source %s   \n"
    if env.sh == "dash":
        sourcePattern = ". %s\n"

    return "".join(sourcePattern % path for path in willSource)
