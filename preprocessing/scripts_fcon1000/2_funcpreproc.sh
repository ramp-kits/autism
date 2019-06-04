#!/usr/bin/env bash

##########################################################################################################################
## SCRIPT TO PREPROCESS THE FUNCTIONAL SCAN
## parameters are passed from 0_preprocess.sh
##
## Written by the Underpants Gnomes (a.k.a Clare Kelly, Zarrar Shehzad, Maarten Mennes & Michael Milham)
## for more information see www.nitrc.org/projects/fcon_1000
##
##########################################################################################################################

## subject
subject=$1
## analysisdirectory/subject
dir=$2
## name of the resting-state scan
rest=$3
## first timepoint (remember timepoint numbering starts from 0)
TRstart=$4
## last timepoint
TRend=$5
## TR
TR=$6

## set your desired spatial smoothing FWHM - we use 6 (acquisition voxel size is 3x3x4mm)
FWHM=6
sigma=`echo "scale=10 ; ${FWHM}/2.3548" | bc`

## Set high pass and low pass cutoffs for temporal filtering
hp=0.005
lp=0.1

## directory setup
func_dir=${dir}/session_1/rest_1

##########################################################################################################################
##---START OF SCRIPT----------------------------------------------------------------------------------------------------##
##########################################################################################################################

# setting highpass if useful
if [[ `perl -e "print 1 / (($TRend - $TRstart) * $TR) < $hp"` ]]; then
    highpass="-highpass ${hp}"
else
    highpass=""
fi

echo ---------------------------------------
echo !!!! PREPROCESSING FUNCTIONAL SCAN !!!!
echo ---------------------------------------

cwd=$( pwd )
cd ${func_dir}

## 1. Dropping first # TRS
echo "Dropping first TRs"
3dcalc -a ${rest}.nii.gz[${TRstart}..${TRend}] -expr 'a' -prefix ${rest}_dr.nii.gz

##2. Deoblique
echo "Deobliquing ${subject}"
3drefit -deoblique ${rest}_dr.nii.gz

##3. Reorient into fsl friendly space (what AFNI calls RPI)
echo "Reorienting ${subject}"
3dresample -orient RPI -inset ${rest}_dr.nii.gz -prefix ${rest}_ro.nii.gz

##4. Motion correct to average of timeseries
echo "Motion correcting ${subject}"
3dTstat -mean -prefix ${rest}_ro_mean.nii.gz ${rest}_ro.nii.gz 
3dvolreg -Fourier -twopass -base ${rest}_ro_mean.nii.gz -zpad 4 -prefix ${rest}_mc.nii.gz -1Dfile ${rest}_mc.1D ${rest}_ro.nii.gz

##5. Remove skull/edge detect
echo "Skull stripping ${subject}"
3dAutomask -prefix ${rest}_mask.nii.gz -dilate 1 ${rest}_mc.nii.gz
3dcalc -a ${rest}_mc.nii.gz -b ${rest}_mask.nii.gz -expr 'a*b' -prefix ${rest}_ss.nii.gz

##6. Get eighth image for use in registration
echo "Getting example_func for registration for ${subject}"
3dcalc -a ${rest}_ss.nii.gz[7] -expr 'a' -prefix example_func.nii.gz

##7. Spatial smoothing
echo "Smoothing ${subject}"
fslmaths ${rest}_ss.nii.gz -kernel gauss ${sigma} -fmean -mas ${rest}_mask.nii.gz ${rest}_sm.nii.gz

##8. Grandmean scaling
echo "Grand-mean scaling ${subject}"
fslmaths ${rest}_sm.nii.gz -ing 10000 ${rest}_gms.nii.gz -odt float

##9. Temporal filtering
echo "Band-pass filtering ${subject}"
cmd="3dFourier -lowpass ${lp} $highpass -retrend -prefix ${rest}_filt.nii.gz ${rest}_gms.nii.gz"
echo "$cmd"
eval "$cmd"

##10.Detrending
echo "Removing linear and quadratic trends for ${subject}"
3dTstat -mean -prefix ${rest}_filt_mean.nii.gz ${rest}_filt.nii.gz
3dDetrend -polort 2 -prefix ${rest}_dt.nii.gz ${rest}_filt.nii.gz
3dcalc -a ${rest}_filt_mean.nii.gz -b ${rest}_dt.nii.gz -expr 'a+b' -prefix ${rest}_pp.nii.gz

##11.Create Mask
echo "Generating mask of preprocessed data for ${subject}"
fslmaths ${rest}_pp.nii.gz -Tmin -bin ${rest}_pp_mask.nii.gz -odt char

cd ${cwd}
