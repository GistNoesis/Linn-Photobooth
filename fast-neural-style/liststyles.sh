#!/bin/bash
for i in $( ls -tr stylemodel/*.t7); do
	filename=$(basename "$i")
	extension="${filename##*.}"
	filename="${filename%.*}"
	echo \"$filename\",
done