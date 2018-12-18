#!/usr/bin/env bash

##########################################################################################################################
## SCRIPT TO DO IMAGE REGISTRATION
## parameters are passed from 0_preprocess.sh
##
## !!!!!*****ALWAYS CHECK YOUR REGISTRATIONS*****!!!!!
##
##
## Written by the Underpants Gnomes (a.k.a Clare Kelly, Zarrar Shehzad, Maarten Mennes & Michael Milham)
## for more information see www.nitrc.org/projects/fcon_1000
##
##########################################################################################################################

## subject
subject=$1
## analysisdir/subject
dir=$2
## name of anatomical scan
anat=$3
##standard brain to be used in registration
standard=$4
#standard=${FSLDIR}/data/standard/MNI152_T1_3mm_brain.nii.gz

## directory setup
anat_dir=${dir}/session_1/anat_1
func_dir=${dir}/session_1/rest_1
reg_dir=${dir}/session_1/reg


##########################################################################################################################
##---START OF SCRIPT----------------------------------------------------------------------------------------------------##
##########################################################################################################################

echo ------------------------------
echo !!!! RUNNING REGISTRATION !!!!
echo ------------------------------


cwd=$( pwd )

mkdir ${reg_dir}

## 1. Copy required images into reg directory
### copy anatomical
cp ${anat_dir}/${anat}_brain.nii.gz ${reg_dir}/highres.nii.gz
### copy standard
cp ${standard} ${reg_dir}/standard.nii.gz
### copy example func created earlier
cp ${func_dir}/example_func.nii.gz ${reg_dir}/

## 2. cd into reg directory
cd ${reg_dir}

## 3. FUNC->T1
## You may want to change some of the options
flirt -ref highres -in example_func -out example_func2highres -omat example_func2highres.mat -cost corratio -dof 6 -interp trilinear
# Create mat file for conversion from subject's anatomical to functional
convert_xfm -inverse -omat highres2example_func.mat example_func2highres.mat

## 4. T1->STANDARD
## NOTE THAT THIS IS Linear registration, you may want to use FNIRT (non-linear)
flirt -ref standard -in highres -out highres2standard -omat highres2standard.mat -cost corratio -searchcost corratio -dof 12 -interp trilinear
## Create mat file for conversion from standard to high res
convert_xfm -inverse -omat standard2highres.mat highres2standard.mat

## 5. FUNC->STANDARD
## Create mat file for registration of functional to standard
convert_xfm -omat example_func2standard.mat -concat highres2standard.mat example_func2highres.mat
## apply registration
flirt -ref standard -in example_func -out example_func2standard -applyxfm -init example_func2standard.mat -interp trilinear
## Create inverse mat file for registration of standard to functional
convert_xfm -inverse -omat standard2example_func.mat example_func2standard.mat


###***** ALWAYS CHECK YOUR REGISTRATIONS!!! YOU WILL EXPERIENCE PROBLEMS IF YOUR INPUT FILES ARE NOT ORIENTED CORRECTLY (IE. RPI, ACCORDING TO AFNI) *****###

cd ${cwd}
