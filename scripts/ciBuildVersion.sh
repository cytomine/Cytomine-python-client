#!/bin/bash

set -o xtrace
set -o errexit

srcRoot=$(git rev-parse --show-toplevel)
cd $srcRoot

# get version number from git
gitLongTag=$(git describe --long --dirty --tags)
branchName=${1:-$(git rev-parse --abbrev-ref HEAD)} #if no argument defined, get the branch name from git

echo "BANCH NAME IS '$branchName'"
#in the master branch, make sure the tag is clean ('1.2.3'; not 1.2.3-alpha) and there has been 0 commits since the tag has been set.
if [[ $gitLongTag =~ v[0-9]+.[0-9]+.[0-9]+-0-[0-9a-g]{8,9}$ ]]; then

  versionNumber=$(echo $gitLongTag | sed -r "s/v([0-9]+\.[0-9]+\.[0-9]+)-[0-9]+-.+/\1/")

else
  echo "WARNING: invalid tag for a real release $gitLongTag"

  versionNumber=0.0.0-$branchName-$(date "+%Y%m%d%H%M%S")-SNAPSHOT

fi

echo $versionNumber > ./ci/version