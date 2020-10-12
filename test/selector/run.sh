if [ -z "$tmpdir" ]; then
  exit 5
fi

echo "tmpdir: $tmpdir"

# so:/a/23673883/2514354
join() {
    # $1 is sep
    # $2... are the elements to join
    # return is in global variable join_ret
    local sep=$1 IFS=
    join_ret=$2
    shift 2 || shift $(($#))
    join_ret+="${*/#/$sep}"
    echo "$join_ret"
}

# v Never run
# python test/selector/test.py "$tmpdir" | tee \
# >(sort -u \
#   grep -Ff <(join_by $'\n' ${yes[@]}) | wc -l | read -r ycount)
# >(grep -Ff <(join_by $'\n' ${no[@]})  | wc -l | read -r ncount)
# >(wc -l | read -r totalcount)

# echo yes-count: $ycount
# echo no-count: $ncount
# echo total-count: $totalcount
# ^ Never run

read -rd$'\e' check_dot_py << HereDocumentDelimiter
import sys

yesSet= {"source " + s for s in ("$(join '", "' ${yes[@]})")} - set([""])
noSet = {"source " + s for s in ("$(join '", "' ${no[@]} )")}

assert yesSet & noSet == set(), "yesSet & noSet: %s" % (yesSet & noSet)

pathInput = sys.argv[1].strip()
pathList = pathInput.split("\n")
pathSet = set(pathList)

if len(pathList) < 4:
    print("pathInput:\n{}\n".format(pathInput))

if len(pathSet) == 0 and len(yesSet) > 0:
    print("ERROR: pathSet is empty")
    sys.exit(2)
elif pathSet != yesSet:
    fpositive = pathSet - yesSet
    fnegative = yesSet - pathSet
    print("ERROR: pathSet != yesSet")
    print("result - wanted (false positive) ({}):".format(len(fpositive)))
    print("\n".join(fpositive))
    print("")
    print("wanted - result (false negative) ({}):".format(len(fnegative)))
    print("\n".join(fnegative))
    sys.exit(2)
assert pathSet & noSet == set(), "pathSet & noSet: %s" % (pathSet & noSet)

print("1 test OK")

HereDocumentDelimiter

read -rd$'\e' output <<< "$(python "$sc_root_dir"/selector-test.py "$tmpdir")"

echo Result check:

python <(echo "${check_dot_py}") "$output" | sed s:"$tmpdir":'$t':g
