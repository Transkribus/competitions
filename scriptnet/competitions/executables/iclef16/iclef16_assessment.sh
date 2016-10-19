#!/bin/bash

### Configuration ###
GT_DIR="$1";
RES_FILE="$2";
FN="${0##*/}"
ASSESS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )";
ERR="0";

### Error function ###
throw_error () { [ "$1" != "" ] && echo "$FN: error: $1" 1>&2; exit 1; };

### Check arguments, results and ground truth ###
[ "$#" != 2 ] &&
  throw_error $'incorrect input arguments\nUsage: '"$FN GT_DIR RES_FILE";
[ ! -f "$RES_FILE" ] &&
  throw_error "results file does not exist: $RES_FILE";
[ "$(find "$RES_FILE" -size +8M)" != "" ] &&
  throw_error "expected results file size to be less than 8MB";
for f in uses_external_training uses_provided_nbest uses_provided_lines query_by_example; do
  [ $(grep -cE "^# +$f: +(yes|no)" "$RES_FILE") = 0 ] &&
    throw_error "expected results file to include: # $f: +(yes|no)";
done
[ ! -d "$GT_DIR" ] &&
  throw_error "ground truth directory does not exist: $GT_DIR";
for f in line2page_test.txt queries_devel.txt queries_testoov.txt groundtruth_devel.txt groundtruth_devel_broken.txt groundtruth_devel_oov.txt; do
  [ ! -f "$GT_DIR/$f" ] &&
    throw_error "ground truth file does not exist: $GT_DIR/$f";
done

### Create temporal directory ###
TMP="${TMPDIR:-/tmp}";
TMP=$(mktemp -d --tmpdir="$TMP" ${FN%.*}_XXXXX);
[ ! -d "$TMP" ] &&
  throw_error "failed to create temporal directory: $TMP";

### Keep only development set results ###
awk '{ if( $1 == "#" || ( $2 <= 10584 && $1 <= 510 ) ) print; }' "$RES_FILE" \
  > "$TMP/results_devel.txt";

### Only results with broken words ###
grep -F / "$TMP/results_devel.txt" > "$TMP/results_devel_broken.txt";

### Qnly results for OOV queries ###
awk '{ if(ARGIND==1)q[$1]="";else if($1 in q)print; }' "$GT_DIR/queries_testoov.txt" "$TMP/results_devel.txt" \
  > "$TMP/results_devel_oov.txt";

### Technique characteristics ###
sed -rn '/^# +(uses_|query_)/{ s|^# *|iclef16_|; s|:||; s| +| |g; p; }' "$RES_FILE";

### Performance measures: complete development set ###
"$ASSESS_DIR/assessment.py" --query-list "$GT_DIR/queries_devel.txt" "$GT_DIR/line2page_test.txt" "$TMP/results_devel.txt" "$GT_DIR/groundtruth_devel.txt" \
  | sed 's|-Level |_|; s|Mean |m|; s|Global |g|; s| =||;' \
  | awk '{ printf("iclef16_Complete_%s %.1f\n",$1,100*$2) }';
R=("${PIPESTATUS[@]}");
[ "${R[0]}" != 0 ] && ERR=$((ERR+1));

### Performance measures: broken words development set ###
if [ "$ERR" = 0 ] && [ -s "$TMP/results_devel_broken.txt" ]; then
  "$ASSESS_DIR/assessment.py" --query-list "$GT_DIR/queries_devel.txt" "$GT_DIR/line2page_test.txt" "$TMP/results_devel_broken.txt" "$GT_DIR/groundtruth_devel_broken.txt" \
    | sed 's|-Level |_|; s|Mean |m|; s|Global |g|; s| =||;' \
    | awk '{ printf("iclef16_Broken_%s %.1f\n",$1,100*$2) }';
  R=("${PIPESTATUS[@]}");
  [ "${R[0]}" != 0 ] && ERR=$((ERR+1));
fi

### Performance measures: oov queries development set ###
if [ "$ERR" = 0 ] && [ -s "$TMP/results_devel_oov.txt" ]; then
  "$ASSESS_DIR/assessment.py" --query-list "$GT_DIR/queries_testoov.txt" "$GT_DIR/line2page_test.txt" "$TMP/results_devel_oov.txt" "$GT_DIR/groundtruth_devel_oov.txt" \
    | sed 's|-Level |_|; s|Mean |m|; s|Global |g|; s| =||;' \
    | awk '{ printf("iclef16_OOV_%s %.1f\n",$1,100*$2) }';
  R=("${PIPESTATUS[@]}");
  [ "${R[0]}" != 0 ] && ERR=$((ERR+1));
fi

### Remove temporal files ###
rm -r "$TMP";

### Report error ###
[ "$ERR" != 0 ] &&
  throw_error "problems computing performance measures";
exit 0;
