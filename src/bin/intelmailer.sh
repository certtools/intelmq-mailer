#! /bin/sh
set -x

SCRIPTDIR=$(dirname $0)
BASEDIR=$(dirname $SCRIPTDIR)

echo "SCRIPT: $SCRIPTDIR"
echo "BASE: $BASEDIR"

export PYTHONPATH=$BASEDIR:$PYTHONPATH

python $BASEDIR/management/new_manager.py
