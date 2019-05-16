#!/usr/bin/env bash

##########################################################################################################################
## SCRIPT TO RUN GENERAL RESTING-STATE PREPROCESSING
##
## This script can be run on its own, by filling in the appropriate parameters
## Alternatively this script gets called from batch_process.sh, where you can use it to run N sites, one after the other.
##
## Written by the Underpants Gnomes (a.k.a Clare Kelly, Zarrar Shehzad, Maarten Mennes & Michael Milham)
## for more information see www.nitrc.org/projects/fcon_1000
##
##########################################################################################################################

##########################################################################################################################
## PARAMETERS
## 
## Either set them yourself for single site preprocessing or leave as is for batch_process.sh
##
##########################################################################################################################
## directory where scripts are located
scripts_dir=$1
## full/path/to/site
analysisdirectory=$2
## full/path/to/site/subject_list
subject_list=$3
## name of anatomical scan (no extension)
anat_name=$4
## name of resting-state scan (no extension)
rest_name=$5
## what is the first volume, default is 0
first_vol=$6
## what is the last volmue. Should equal (n volumes - 1)
last_vol=$7
## what is the number of volumes
n_vols=$8
## TR
TR=$9
## shift parameters one to the left; comment if not running batch_process.sh
shift
## Standard brain
standard_brain=$9
##########################################################################################################################


##########################################################################################################################
##---START OF SCRIPT----------------------------------------------------------------------------------------------------##
##########################################################################################################################


## Get subjects to run
subjects=$( cat ${subject_list} )

## SUBJECT LOOP
for subject in $subjects
do

echo preprocessing $subject

##################################################################################################################################
## preprocess anatomical scan
## subject - full path to subject directory, subject is paremeterized - name of anatomical scan (no extension)
##################################################################################################################################
${scripts_dir}/1_anatpreproc.sh ${subject} ${analysisdirectory}/${subject} ${anat_name}

##################################################################################################################################
## preprocess functional scan
## subject - full path to subject directory, subject is parameterized - name of functional scan (no extension) -
## first volume - last volume - TR
## set temporal filtering and spatial smoothing in 2_funcpreproc.sh (default is 0.005-0.1Hz and 6 FWHM)
##################################################################################################################################
${scripts_dir}/2_funcpreproc.sh ${subject} ${analysisdirectory}/${subject} ${rest_name} ${first_vol} ${last_vol} ${TR}

##################################################################################################################################
## registration
## subject - full path to subject directory, subject is parameterized - name of anatomical scan (no extension) - standard brain
##################################################################################################################################
${scripts_dir}/3_registration.sh ${subject} ${analysisdirectory}/${subject} ${anat_name} ${standard_brain}

##################################################################################################################################
## segmentation
## subject - full path to subject directory, subject is parameterized - name of anatomical scan (no extension) -
## name of resting-state scan (no extension) - full path to tissueprior dir
##################################################################################################################################
${scripts_dir}/4_segment.sh ${subject} ${analysisdirectory}/${subject} ${anat_name} ${rest_name} ${scripts_dir}/tissuepriors/3mm/

##################################################################################################################################
## nuisance signal regression
## subject - full path to subject directory, subject is parameterized - name of resting-state scan (no extension) -
## TR - number of volumes (default = last_vol + 1; has to be +1 since volume numbering starts at 0) -
## full path to dir where feat model template fsf file is located
##################################################################################################################################
${scripts_dir}/5_nuisance.sh ${subject} ${analysisdirectory}/${subject} ${rest_name} ${TR} ${n_vols} ${scripts_dir}/templates/nuisance.fsf

## END OF SUBJECT LOOP
done
