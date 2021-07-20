#!/bin/bash
for f in *.cnv; do 
    if grep -q XBT "$f"; then
        echo $f is an xbt # SomeString was found
        filen=$(echo $f | cut -c 1-15)
        echo $filen    
        fi
    #echo $file
    #line=$(head -1 $f)
    #echo $line
	#find the filename 
	#filen=$(echo $file | cut -c 1-8)
    #echo $filen
	#echo $filen
	#head -1 $file
    #line=$(head -1 $file)
	#echo $line
done




#LST=$(ls *.cnv)
#for FILE in ${LST} ; do
#    echo ${FILE}
#    #line=$(head -1 ${FILE})
#    #echo ${line}
#    head -1 ${FILE} | read LINE
#    echo ${LINE}
#done
