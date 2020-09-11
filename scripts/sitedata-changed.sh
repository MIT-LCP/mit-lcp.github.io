something_changed=`git diff-index --exit-code HEAD | grep sitedata`

if [ -n "$something_changed" ]
then
    echo >&2 "\nChanges to sitedata detected. Continuing build.\n"
    exit 0
else
    echo >&2 "\nNo changes to sitedata detected. Finishing build.\n"
    git checkout dev
    exit 1
fi
