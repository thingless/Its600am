#!/bin/bash
if [ $# -ne 2 ];
    then echo "usage: build_data_for_city.sh CITY_NAME GMAPSKEY"
    exit 1
fi

GMAPSKEY=$2
CITY_NAME=$1
FILE_NAME=$(echo $CITY_NAME | sed 's/ /_/g')
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo -e {0..23}{00,30}"\n" | sed 's/ //g' | parallel ./build_data.py --gmapskey "$GMAPSKEY" --location "'""$CITY_NAME""'" --day 5 --time "{}" | jq -c -s . > "$FILE_NAME".json