#!/usr/bin/env bash
# Test bdrc app parser  on DB Apps
#
#set -v
#set -x


#Create a tmp place
home_d=$(mktemp -d)

pushd $home_d
python3 -m venv py-test
. py-test/bin/activate
# Install the test subject
pip install --force-reinstall --no-cache-dir -i https://test.pypi.org/simple/ bdrc-DBAppParser
#
# Install a test suite. Shouldn't reinstall bdrcDBApps
pip install --no-cache-dir bdrc-DBApps

default_db_config=~/.config/bdrc/db_apps.config
non_exist_config=/dev/null/db_config


which getReadyRelated
test_comment="Test using default_db_config ${default_db_config}"
if [ -r  "${default_db_config}" ] ; then
    echo Testing default config
    getReadyRelated -o -n 4 grr
    tr=PASS
    if ! grep 'WorkName,HOLLIS' grr ; then
      tr=FAIL
    fi
    echo $tr $test_comment
fi

test_comment="Test using known nonexistent config"
rm grr
tr=PASS
if getReadyRelated -d fake:${non_exist_config}  -o -n 3 grr ; then
  tr=FAIL
fi
echo $tr $test_comment
#
deactivate
popd
rm -rf $home_d
echo $home_d








