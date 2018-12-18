#!/usr/bin/env bash

##########################################################################################################################
## SCRIPT TO CALCULATE SEED-BASED RESTING-STATE FUNCTIONAL CONNECTIVITY
##
## This script can be run on its own, by filling in the appropriate parameters
## Alternatively this script gets called from batch_process.sh, where you can use it to run N sites, one after the other.
##
## Written by Clare Kelly, Maarten Mennes & Michael Milham
## for more information see www.nitrc.org/projects/fcon_1000
##
##########################################################################################################################


## analysisdirectory
dir=$1
## full/path/to/subject_list.txt containing subjects you want to run
subject_list=$2
## image to extract timeseries from. default = rest_res.nii.gz
postprocessing_image=$3
## name of resting-state scan (no extenstion)
rest=$4
## file containing list with full/path/to/seed.nii.gz
seed_list=$5
## standard brain as reference for registration
standard=$6

## directory setup
## see below


##########################################################################################################################
##---START OF SCRIPT----------------------------------------------------------------------------------------------------##
##########################################################################################################################


## Get subjects to run
subjects=$( cat ${subject_list} )
## Get seeds to run
seeds=$( cat ${seed_list} )

## A. SUBJECT LOOP
for subject in $subjects
do

## directory setup
func_dir=${dir}/${subject}/session_1/rest_1
reg_dir=${dir}/${subject}/session_1/reg
## seed_timeseries
seed_ts_dir=${dir}/${subject}/session_1/rest_1/seed_ts
## RSFC maps
RSFC_dir=${dir}/${subject}/session_1/rest_1/RSFC


echo --------------------------
echo running subject ${subject}
echo --------------------------

mkdir -p ${seed_ts_dir}
mkdir -p ${RSFC_dir}

## B. SEED_LOOP
for seed in $seeds
do

seed_name=$( echo ${seed##*/} | sed s/\.nii\.gz//g )
echo \------------------------
echo running seed ${seed_name}
echo \------------------------

## Check if seed might have already been run
if [ -f ${RSFC_dir}/${seed_name}_Z_2standard.nii.gz ]; then echo final file for seed ${seed_name} already exists; continue; fi

## 1. Extract Timeseries
echo Extracting timeseries for seed ${seed_name}
3dROIstats -quiet -mask_f2short -mask ${seed} ${func_dir}/${rest}_res2standard.nii.gz > ${seed_ts_dir}/${seed_name}.1D

## 2. Compute voxel-wise correlation with Seed Timeseries		
echo Computing Correlation for seed ${seed_name}
3dfim+ -input ${func_dir}/${postprocessing_image} -ideal_file ${seed_ts_dir}/${seed_name}.1D -out Correlation -bucket ${RSFC_dir}/${seed_name}_corr.nii.gz

## 3. Z-transform correlations		
echo Z-transforming correlations for seed ${seed_name}
3dcalc -a ${RSFC_dir}/${seed_name}_corr.nii.gz -expr 'log((a+1)/(a-1))/2' -prefix ${RSFC_dir}/${seed_name}_Z.nii.gz

## 4. Register Z-transformed correlations to standard space
echo Registering Z-transformed map to standard space
flirt -in ${RSFC_dir}/${seed_name}_Z.nii.gz -ref ${standard} -applyxfm -init ${reg_dir}/example_func2standard.mat -out ${RSFC_dir}/${seed_name}_Z_2standard.nii.gz


## END OF SEED LOOP
done

## END OF SUBJECT LOOP
done
