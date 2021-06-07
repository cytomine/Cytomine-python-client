#!/bin/bash

set -o xtrace
set -o errexit

srcRoot=$(git rev-parse --show-toplevel)
cd $srcRoot

# get version number from git
gitLongTag=$(git describe --long --dirty)
# get the branch name from first arg or from git
branchName=${1:-$(git rev-parse --abbrev-ref HEAD)}

# check if tag is an official release (v1.2.3) + no other commit behind (or dirty)
if [[ $gitLongTag =~ v[0-9]+.[0-9]+.[0-9]+-0-[0-9a-g]{8,9}$ ]]; then
  versionNumber=$(echo $gitLongTag | sed -r "s/v([0-9]+\.[0-9]+\.[0-9]+)-[0-9]+-.+/\1/")
else
  echo "WARNING: invalid tag for an official release $gitLongTag"
  versionNumber=$branchName-$(date "+%Y%m%d%H%M%S")-SNAPSHOT
fi

echo $versionNumber > ./ci/version
