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

read -rd$'\e' check_py << HereDocumentDelimiter
import sys

yesSet={"source " + s for s in ("$(join '", "' ${yes[@]})")}
noSet ={"source " + s for s in ("$(join '", "' ${no[@]} )")}

assert yesSet & noSet == set(), "yesSet & noSet: %s" % (yesSet & noSet)

testSet=set(sys.stdin.read().split("\n"))

if testSet != yesSet | {""}:
    print("ERROR: testSet != yesSet")
    print("ts - ys:")
    print("\n".join(testSet - yesSet))
    print("")
    print("ys - ts: %s")
    print("\n".join(yesSet - testSet))
    sys.exit(2)
assert testSet & noSet == set(), "testSet & noSet: %s" % (testSet & noSet)

print("1 test OK")

HereDocumentDelimiter

python "$dir"/selector-test.py "$tmpdir" \
| python <(echo "${check_py}")