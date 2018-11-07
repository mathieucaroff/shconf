# About this directory

This directory contains a template to make multiphase tests.

The entry point is `main.sh`. It runs each phase by sourcing each of the 3
other files:

* `prepare.sh` which setup the environment for the test
* `test.sh` which executes the test
* `teardown.sh` which undoes what `prepare.sh` did.