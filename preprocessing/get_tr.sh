#!/bin/bash
set -e

fcon=$1
outfile=$2

echo -e "participant_id\tsession_id\trun_id\trepetition_time" > "$outfile"
for rs in "$fcon"/*/*/run_?/session_?/rest_1/rest.nii.gz; do
	rt=$(fslinfo "$rs" | awk '$1=="pixdim4"{print $2}')
	if [[ "$rs" =~ /([^/]+)/run_(.)/session_(.)/rest_1 ]]; then
		subject=${BASH_REMATCH[1]}
		session=${BASH_REMATCH[3]}
		run=${BASH_REMATCH[2]}
		echo -e "$subject\t$session\t$run\t$rt" >> "$outfile"
	else
		echo "error parsing nifti path" >&2
		exit 1
	fi
done
