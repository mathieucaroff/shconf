#!/bin/bash

SOURCE="$(readlink -f ${BASH_SOURCE:-0})"
selector_dir="${SOURCE%/*}"
test_dir="${selector_dir%/*}"
sc_root_dir="${test_dir%/*}"
dir="${sc_root_dir}"

tmpdir="/tmp/sc-selector-$RANDOM"
mkdir "$tmpdir" || exit 1

cd "$dir"
source "$selector_dir"/prepare.sh
cd "$dir"
source "$selector_dir"/test.sh
cd "$dir"
source "$selector_dir"/teardown.sh

rm -r "$tmpdir"