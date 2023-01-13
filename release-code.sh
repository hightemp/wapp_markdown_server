#!/bin/bash

CFILE=wapp_markdown_server
timestamp=$(date +%s)
VERSION=$(echo `cat VERSION`.$timestamp)

git add .
git commit -am "`date` update"
git tag $VERSION
git push

if [ "$?" != "0" ]; then
    echo "====================================================="
    echo "ERROR"
    echo
    exit 1
fi

echo "[!] " gh release create $VERSION -t $VERSION -n '""' --target main
gh release create $VERSION -t $VERSION -n "" --target main

if [ "$1" == "pyinst" -o "$1" == "all" ]; then
    ./build.sh pyinst
    cp dist/__main__ ../"${CFILE}.bin"
    gh release upload $VERSION ../"${CFILE}.bin" --clobber
elif [ "$1" == "pyinst_docker" -o "$1" == "all" ]; then
    ./build.sh pyinst_docker
    cp dist/__main__ ../"${CFILE}__all.bin"
    gh release upload $VERSION ../"${CFILE}.bin" --clobber
elif [ "$1" == "zipapp" -o "$1" == "all" ]; then
    ./build.sh zipapp
    gh release upload $VERSION ../"${CFILE}.pyz" --clobber
fi
