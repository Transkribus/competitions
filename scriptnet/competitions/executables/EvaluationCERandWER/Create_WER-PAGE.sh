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
PAGEFORMAT=`pwd`"/competitions/executables/EvaluationCERandWER/page_format_tool"
#[ -z "$PAGEFORMAT" ] && { echo "ERROR: \"page_format_tool\" soft is not installed/found "'!' 1>&2; exit 1; }

mkdir /tmp/trans-hip_$R
mkdir /tmp/trans_$R

cd $D/$2
for f in `find . -name *.zip`; do unzip -o $f; done 
cp $D/$2/*.txt /tmp/trans_${R}/

mkdir /tmp/Results_${R}
cp $D/$1 /tmp/Results_${R}
cd /tmp/Results_${R}
name=`basename $1`
tar -xf $name


for F in `find . -name "*.xml"`; do 
  n=`basename $F`;
  $PAGEFORMAT -i $D/$2/${n/.xml/.JPG} -l ${F} -m FILE || \
      {
        echo "ERROR: \"page_format_tool\" with sample ${F/\.$IEXT/.JPG}" 
        cd ..; continue
      }
  for f in `find . -name "*.txt"`; do  mv $f /tmp/trans-hip_${R}; done
  #rm *png;
done
cd ..

for file in `find /tmp/trans-hip_${R} -name "*.txt"`; 
do


   NAME=/tmp/trans_${R}/$(basename $file)

   awk '{if (NR>=1) printf("%s",$0);}END{printf(" $ ")}' $NAME
   awk '{if (NR>=1) printf("%s ",$0);}END{printf("\n")}' $file

done |ascii2uni -a K 2> /tmp/kk_${R} | sed 's/\x22\x27\x22/\x27/g' | sed 's/\x27\x22\x27/\x22/g' | sed 's/\([0-9]\) \([0-9]\)/\1\2/g' | sed 's/\([0-9]\) \([0-9]\)/\1\2/g' | sed 's/[<>]//g' | sed 's/  / /g' > /tmp/fich_results_${R} 

sed 's/\([.,:;]\)/ \1/g' /tmp/fich_results_${R}  > /tmp/fich_results_WER_${R}

sed 's/^ //g;s/ $//g;s/ [ ]*/ /g;s/ \$ /\$/g' /tmp/fich_results_${R} | sed 's/ /@/g' | sed 's/\(.\)\(.\)/\1 \2 /g' > /tmp/fich_results_CER_${R}

$D/competitions/executables/EvaluationCERandWER//tasas /tmp/fich_results_CER_${R} -ie -s " "  -f "$" 
$D/competitions/executables/EvaluationCERandWER/tasas /tmp/fich_results_WER_${R} -ie -s " "  -f "$"
rm -r /tmp/trans-hip_${R}
rm -r /tmp/trans_${R}
rm -r /tmp/Results_${R}
rm /tmp/fich_results_${R} /tmp/fich_results_WER_${R} /tmp/fich_results_CER_${R}
rm /tmp/kk_${R}
