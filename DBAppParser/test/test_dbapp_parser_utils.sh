#!/usr/bin/env bash
# Test bdrc app parser on DBApps
#
#Create a tmp place

#set -v
#set -x


home_d=$(mktemp -d)

pushd $home_d
echo
echo
echo
python3 -m venv py-test
. py-test/bin/activate
# Install the test subject
pip install --force-reinstall --no-cache-dir -i https://test.pypi.org/simple/ bdrc-DBAppParser==1.0.4
#
# Install a test suite. Shouldn't reinstall bdrcDBApps
pip install --no-cache-dir bdrc-util

default_db_config=~/.config/bdrc/db_apps.config
non_exist_config=/dev/null/db_config

b_date1="2001-01-01 00:00:01"
b_date2="2001-02-02 00:00:02"

e_date1="2001-03-03 00:00:03"
e_date2="2001-04-04 00:00:04"

which log_dip

test_comment="Test using default_db_config ${default_db_config}"
if [ -r  "${default_db_config}" ] ; then
    echo Testing default config
     expected_=$(log_dip -b "${b_date1}" -e "${e_date1}" -a DRS -w NoWork -r 1  "NoRealPathSource" "NoRealPathDest")
    tr=PASS
    if [[ -z ${expected_} ]] ; then
      tr=FAIL
    fi
    echo $tr $test_comment
fi

test_comment="Test using known nonexistent config"
tr=PASS
expected_=$(log_dip -d frelm:${non_exist_config} -b "${b_date2}" -e "${e_date2}" -a DRS -w NoWork -r 2)
if [ ! -n ${expected_} ]; then
  tr=FAIL
fi
echo $tr $test_comment

deactivate
popd
rm -rf $home_d








