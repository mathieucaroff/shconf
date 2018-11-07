#!/bin/bash

SOURCE="${BASH_SOURCE:-0}"
dir="$(readlink -f "${SOURCE%/*}")"

tmpdir="/tmp/sc-$RANDOM"
mkdir "$d" || exit 1

cd "$tmpdir"

source "$dir"/prepare.sh
source "$dir"/test.sh
source "$dir"/teardown.sh