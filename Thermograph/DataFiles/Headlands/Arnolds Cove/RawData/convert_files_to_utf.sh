#!/bin/bash

for f in *;  do

extension="${f##*.}"

#echo $extension
#echo ${extension:0:2}

ascext=${extension:0:2}

#echo $extension

if [ "$extension" == "pipe" ] || [ "$extension" == "PRO" ] || [ "$extension" == "DAT" ] || [ "$extension" == "csv" ] || [ "$ascext" == "00" ];  then

	#echo $f
	#echo $extension

	
	#base_file=`basename $f $extension`
	base_file=$(echo "$f" | cut -f 1 -d '.')
	output_file="${base_file}_utf8.${extension}"
        #echo $base_file
	#echo $output_file


	file -i --mime-encoding $f > charsettmp

	charset=`grep 'charset=' charsettmp | awk '{print $3}' | cut -f2 -d=`

	echo $charset

		if [ "$charset" != "us-ascii" ] || [ "$charset" != "utf-8" ]; then
		echo "this is not a us-ascii file, it is charset=$charset"
		iconv -f $charset -t utf-8 $f -o $output_file
		echo $output_file
		fi

mv $f ./windows_files/.
fi

rm charsettmp

#grep 'charset=' $f | awk '{print $3}' | cut -f2 -d=

done

