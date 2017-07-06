#!/bin/bash

export PATH=$PATH:export PATH=$PATH:$HOME/HTR/bin:`pwd`:.

if [ $# -ne 2 ]; then
 echo "Uso: ${0##*/} <Results-tar-file> <Labels-tar-file>" 
 exit
fi

D=`pwd`
R=`echo $RANDOM`

if [ `file $1 | grep "tar" | wc -l` -ne 1 ] ; then echo "ERROR: the Results file is not a tarball" 1>&2; exit 1; fi
#if [ `file $2 | grep "tar" | wc -l` -ne 1 ] ; then echo "ERROR: the GT file is not a tarball" 1>&2; exit 1; fi


#PAGEFORMAT=$(which page_format_tool)
PAGEFORMAT=`pwd`"/competitions/executables/EvaluationBLEU/page_format_tool"
#[ -z "$PAGEFORMAT" ] && { echo "ERROR: \"page_format_tool\" soft is not installed/found "'!' 1>&2; exit 1; }

mkdir /tmp/hip_$R
mkdir /tmp/ref_$R

cd $D/$2
#for f in `find . -name *.zip`; do unzip -o $f; done 
cp $D/$2/*.txt $D/$2/*.xml /tmp/ref_${R}/

mkdir /tmp/Results_${R}
cp $D/$1 /tmp/Results_${R}
cd /tmp/Results_${R}
name=`basename $1`
tar -xf $name


for F in `find . -name "*.xml"`; do 
  n=`basename $F`;
  $PAGEFORMAT -i $D/$2/${n/.xml/.JPG} -l ${F} -m FILE > /dev/null || \
      {
        echo "ERROR: \"page_format_tool\" with sample ${F/\.$IEXT/.JPG}" 
        cd ..; continue
      }
  for f in `find . -name "*.txt"`; do  mv $f /tmp/hip_${R}; done
  #rm *png;
done
cd ..

for file in /tmp/ref_${R}/*xml; do 
   n=`basename ${file/.xml/}`; 
   for i in /tmp/ref_${R}/${n}*txt; do 
	cat $i;
   done | sed 's/\([.,:;]\)/ \1/g' >> /tmp/ref_${R}/reference.txt;
   echo "" >> /tmp/ref_${R}/reference.txt;


   if [ -e /tmp/Results_${R}/${n}.xml ] ; then 
	for j in /tmp/hip_${R}/${n}*txt; do 
	        cat $j;
   	done | sed 's/\([.,:;]\)/ \1/g' >> /tmp/hip_${R}/hipotesis.txt;
        echo "" >> /tmp/hip_${R}/hipotesis.txt
   else
	echo "" >> /tmp/hip_${R}/hipotesis.txt;
   fi
done 

perl $D/competitions/executables/EvaluationBLEU/multi-bleu.perl /tmp/ref_${R}/reference.txt < /tmp/hip_${R}/hipotesis.txt

#rm -r /tmp/hip_${R}
#rm -r /tmp/ref_${R}
#rm -r /tmp/Results_${R}
