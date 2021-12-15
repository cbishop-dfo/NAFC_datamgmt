#!/bin/bash

filename="ListInstrumentsUsed.txt"
oxyfile="oxy_instr_list.txt"
if [ -f $filename ]; then rm $filename; fi
if [ -f $oxyfile ]; then rm $oxyfile; fi

if [ -f *.bot ]; then
	shiptrip=$(ls *.bot | cut -c 1-5)
	#printf "%s%s\n" "Instruments used on " "$shiptrip"
	#printf "%s%s\n" "Instruments used on " "$shiptrip" >> $filename
fi
printf "%s\t%s\t%s\t%s\t%s\t%s\n" "Filename" "Comment" "Instr" "Instr" "PrimOSens" "SecOSens"
printf "%s\t%s\t%s\t%s\t%s\t%s\n" "Filename" "Comment" "Instr" "Instr" "PrimOSens" "SecOSens" >>$filename
printf "%s,%s,%s,%s,%s,%s\n" "Filename" "Instr" "PrimOSens" "SecOSens" "PrimSOC" "SecSOC" >>$oxyfile

for file in *.sbe; do 

	#find the filename
	filen=$(echo $file | cut -c 1-8)
	echo $filen

	#find the lines with the needed variables
	oxytest1=$(grep -n '<!-- A/D voltage 0, Oxygen, SBE 43 -->' $file | cut -c1-3); 
	oxytest2=$(grep -n '<!-- A/D voltage 2, Oxygen, SBE 43, 2 -->' $file | cut -c1-3)
	comtest=$(grep 'COMMENTS' $file | cut -c 24-36)
	oxyind1=$(($oxytest1+2))
	oxyind2=$(($oxytest2+2))

	#find soc values
	soctest1=$(grep -n '<!-- A/D voltage 0, Oxygen, SBE 43 -->' $file | cut -c1-3); 
	soctest2=$(grep -n '<!-- A/D voltage 2, Oxygen, SBE 43, 2 -->' $file | cut -c1-3)
	socind1=$(($soctest1+16))
	socind2=$(($soctest2+16))
	
	#pick out the sensor numbers
	oxyinst1=$(head -$oxyind1 $file | tail -1 | sed -e 's/<[^>]*>//g' | sed -e 's/ //g' | sed -e 's/#//g') 
	oxyinst2=$(head -$oxyind2 $file | tail -1 | sed -e 's/<[^>]*>//g' | sed -e 's/ //g' | sed -e 's/#//g')
	socinst1=$(head -$socind1 $file | tail -1 | sed -e 's/<[^>]*>//g' | sed -e 's/ //g' | sed -e 's/#//g') 
	socinst2=$(head -$socind2 $file | tail -1 | sed -e 's/<[^>]*>//g' | sed -e 's/ //g' | sed -e 's/#//g')

	#pick out the instrument numbers and separate the variable for manually entered and instrument recorded	
	#ox=$(head -14 $file | tail -1 | sed -e 's/**//g')
	ox=$(head -23 $file | tail -1 | sed -e 's/**//g')
	ox1=$(echo $ox | cut -c 14-17)
	ox2=$(echo $ox | cut -c 22-27)
	ox3=$(echo $ox | cut -c 14-16)
	ox4=$(echo $ox | cut -c 22-27)

	#print the variables to the screen
	printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$filen" "$comtest" "$ox1" "$ox2" "$oxyinst1" "$oxyinst2"
	printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$filen" "$comtest" "$ox1" "$ox2" "$oxyinst1" "$oxyinst2" >> $filename
	printf "%s,%s,%s,%s,%s,%s,%s\n" "$filen" "$ox4" "$oxyinst1" "$oxyinst2" "$socinst1" "$socinst2" >> $oxyfile

done

#remove ^M from the outputted file. Why are these being added? :S
for file in oxy_instr_list.txt; do
    if [ -f "$file" ]; then
    	echo $file
	tr -d '\015' <$file >$file.temporary
	rm $file
	mv $file.temporary $file							        
    fi
done

