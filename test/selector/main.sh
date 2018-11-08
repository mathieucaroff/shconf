#!/bin/bash

SOURCE="$(readlink -f ${BASH_SOURCE:-0})"
selector_dir="${SOURCE%/*}"
test_dir="${selector_dir%/*}"
sc_root_dir="${test_dir%/*}"

tmpdir="/tmp/sc-selector-$RANDOM"
mkdir "$tmpdir" || exit 1

cd "$selector_dir"
source ./prepare.sh
cd "$selector_dir"
source ./run.sh
cd "$selector_dir"
source ./teardown.sh

rm -r "$tmpdir"