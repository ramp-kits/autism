#!/bin/bash
set -e

dataset=$input
output=$dataset

source activate py2

echo "listing subjects..."
subjects=($dataset/*/stats/aseg.stats)
subjects=("${subjects[@]%/stats/aseg.stats}")
subjects=("${subjects[@]##*/}")
echo "done"

SUBJECTS_DIR=$dataset asegstats2table --subjects ${subjects[@]} --skip -m volume -t $output.aseg.csv
SUBJECTS_DIR=$dataset aparcstats2table --subjects ${subjects[@]} --skip --hemi lh -m area -t $output.lh.area.csv
SUBJECTS_DIR=$dataset aparcstats2table --subjects ${subjects[@]} --skip --hemi lh -m thickness -t $output.lh.thickness.csv
SUBJECTS_DIR=$dataset aparcstats2table --subjects ${subjects[@]} --skip --hemi rh -m area -t $output.rh.area.csv
SUBJECTS_DIR=$dataset aparcstats2table --subjects ${subjects[@]} --skip --hemi rh -m thickness -t $output.rh.thickness.csv
