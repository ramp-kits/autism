#!/usr/bin/env bash

##########################################################################################################################
## SCRIPT TO BATCH PROCESS DATASETS INCLUDED IN THE 1000 FUNCTIONAL CONNECTOMES PROJECT
##
## Written by Maarten Mennes & Michael Milham
## for more information see www.nitrc.org/projects/fcon_1000
##
## MAKE SURE TO CHECK/CHANGE ALL PARAMETERS BEFORE RUNNING THE SCRIPT
##
##########################################################################################################################

####################
## scripts directory
####################
## directory where you put the scripts downloaded from www.nitrc.org/projects/fcon_1000
## e.g. /home/fcon_1000/scripts
scripts_dir=$(cd `dirname ${BASH_SOURCE[0]}` && pwd)

###########################
## what do you want to run?
###########################
## 1 - general RSFC preprocessing
## 2 - single-subject RSFC (requires general preprocessing to be completed)
## 3 - ALFF/fALFF (default frequency band of interest is 0.01-0.1Hz)
## 4 - Dual Regression
what_to_do=1


#######################
## some important names
#######################
## anatomical scan you want to use (no extension)
anat_name=anat
## resting-state scan you want to use (no extension)
rest_name=rest


################################################
## Extra parameters needed to run postprocessing
################################################
## image you want to use to calculate RSFC for. 
## This is usually the image containing resting-state scan after regressing out the nuisance parameters
postprocessing_image=rest_res.nii.gz
## path to list of seeds you want to calculate RSFC for e.g. /home/fcon_1000/scripts/my_seeds.txt
## DEFAULT path = within the scripts directory specified above
## the list includes the full path for each seed e.g. /home/my_seeds/connectomes_seed_3mm.nii.gz
seed_list=${scripts_dir}/Fox_seed_list.txt
## image you want to use for postprocessing in MNI space 
## This image is used in the dual regression step. Dual regression is applied to this image. 
postprocessing_mni_image=rest_res2standard.nii.gz
## mask used for Dual Regression; default = MNI based mask
## the resolution has to be consistent with the DR templates
mask=${FSLDIR}/data/standard/MNI152_T1_3mm_brain_mask.nii.gz
## template used for Dual Regression
## default = the metaICA image, including 20 ICA components as derived in Biswal et al. 2010, PNAS
## running Dual Regression is tuned to run for 20 components you will have to edit 8_singlesubjectDR.sh if you want to use a different template
DR_template=${scripts_dir}/templates/metaICA.nii.gz


#######################################
## Standard brain used for registration
## include the /full/path/to/it
#######################################
standard_brain=${FSLDIR}/data/standard/MNI152_T1_3mm_brain.nii.gz


#####################################################################################
## batch processing parameter list
## DO NOT FORGET TO EDIT batch_list.txt itself to include the appropriate directories
#####################################################################################
## path to batch_list.txt, e.g., /home/fcon_1000/scripts/my_batch_list.txt.
## DEFAULT = within the scripts directory specified above
## This file contains the sites (and their parameters) you want to process.
## batch_list.txt contains 1 line per site listing:
## - analysis directory, i.e. full/path/to/site
## - subjectlist, i.e. full/path/to/site/site_subjects.txt
## - first timepoint, default = 0 (start with the 1st volume)
## - last timepoint = number of timepoints - 1 (since count starts at 0)
## - number of timepoints in the timeseries
## - TR
batch_list=${scripts_dir}/lists/batch_list-$1



##########################################################################################################################
##---START OF SCRIPT---------------------------------------------------------------------------------------------------------------------##
##---NO EDITING BELOW UNLESS YOU KNOW WHAT YOU ARE DOING----------------------------------------------------------------##
##########################################################################################################################

while read line
do

## 1. cut site specific parameters from batch_list
analysisdirectory=$( echo $line | cut -d ' ' -f1 )
subject_list=$( echo $line | cut -d ' ' -f2 )
first_vol=$( echo $line | cut -d ' ' -f3 )
last_vol=$( echo $line | cut -d ' ' -f4 )
n_vols=$( echo $line | cut -d ' ' -f5 )
TR=$( echo $line | cut -d ' ' -f6 )

## 2. do the processing asked for
case ${what_to_do} in
1) echo ${analysisdirectory} + ${subject_list} + ${first_vol} + ${last_vol} + ${n_vols} + ${TR}
${scripts_dir}/0_preprocess.sh ${scripts_dir} ${analysisdirectory} ${subject_list} ${anat_name} ${rest_name} ${first_vol} ${last_vol} ${n_vols} ${TR} ${standard_brain}
;;
2) echo ${analysisdirectory} + ${subject_list} + ${postprocessing_image} + ${rest_name} + ${seed_list} + ${standard_brain}
${scripts_dir}/6_singlesubjectRSFC.sh ${analysisdirectory} ${subject_list} ${postprocessing_image} ${rest_name} ${seed_list} ${standard_brain}
;;
3) echo ${analysisdirectory} + ${subject_list} + ${rest_name} + ${n_vols} + ${TR} + ${standard_brain}
${scripts_dir}/7_singlesubjectfALFF.sh ${analysisdirectory} ${subject_list} ${rest_name} ${n_vols} ${TR} ${standard_brain}
;;
4) echo ${analysisdirectory} + ${subject_list} + ${postprocessing_mni_image} + ${DR_template} + ${mask}
${scripts_dir}/8_singlesubjectDR.sh ${analysisdirectory} ${subject_list} ${postprocessing_mni_image} ${DR_template} ${mask}

;;
esac

done < ${batch_list}
