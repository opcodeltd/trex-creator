#!/bin/bash

set -e

PROJECT_ROOT=$(cd $(dirname "$0"); pwd)

cd "$PROJECT_ROOT"
. bin/activate


for file in {,trex/}requirements.txt; do [ -f $file ] && pip install -r $file; done
if [ "$1" == "-d" ]; then
    pip install --use-wheel -r trex/dev-requirements.txt
fi

[ -f package.json ] || cp trex/package.json package.json
mkdir -p node_modules
npm install

[ -f bower.json ] || cp trex/bower.json bower.json
[ -f .bowerrc ] || cp trex/.bowerrc .bowerrc
bower install

exit 0
