#!/usr/bin/env bash

##########################################################################################################################
## SCRIPT TO CALCULATE AMPLITUDE MEASURES OF THE LOW FREQUENCY OSCILLATIONS IN THE BOLD SIGNAL
##
## This script can be run on its own, by filling in the appropriate parameters
## Alternatively this script gets called from batch_process.sh, where you can use it to run N sites, one after the other.
##
## Written by Xi-Nian Zuo, Maarten Mennes & Michael Milham
## for more information see www.nitrc.org/projects/fcon_1000
##
##########################################################################################################################

## analysisdirectory
dir=$1
## full/path/to/subject_list.txt containing subjects you want to run
subject_list=$2
## name of resting-state scan (no extenstion)
rest=$3
## number of timepoints
n_vols=$4
## TR
TR=$5
## standard brain as reference for registration
standard=$6

## set your desired spatial smoothing FWHM - default is 6mm (acquisition voxel size is 3x3x4mm)
FWHM=6
sigma=$( echo "scale=10;${FWHM}/2.3548" | bc )
## frequency band setting: default LP (i.e., low frequency) = 0.01 ; default HP (i.e., high frequency) = 0.1
LP=0.01 ; HP=0.1



##########################################################################################################################
##---START OF SCRIPT----------------------------------------------------------------------------------------------------##
##########################################################################################################################

echo ---------------------------------------
echo !!!! CALCULATING ALFF AND fALFF !!!!
echo ---------------------------------------

cwd=$( pwd )

## Get subjects to run
subjects=$( cat ${subject_list} )
## A. SUBJECT LOOP
for subject in $subjects
do

## directory setup
func_dir=${dir}/${subject}/func
reg_dir=${dir}/${subject}/reg
ALFF_dir=${dir}/${subject}/func/ALFF

echo --------------------------
echo running subject ${subject}
echo --------------------------

mkdir -p ${ALFF_dir} ; cd ${ALFF_dir}

## PREPROCESSING
## 1. Despike
echo "Despiking"
rm -f prefiltered_func_data_dspk.nii.gz
3dDespike -prefix prefiltered_func_data_dspk.nii.gz ${func_dir}/${rest}_ss.nii.gz

## 2. Detrending for linear trends
echo "Removing linear trend in timeseries"
rm -f prefiltered_func_data_rlt.nii.gz
3dTcat -rlt+ -prefix prefiltered_func_data_rlt.nii.gz prefiltered_func_data_dspk.nii.gz

## 3. Spatial Smoothing
echo "Spatial smoothing"
fslmaths prefiltered_func_data_rlt.nii.gz -kernel gauss ${sigma} -fmean prefiltered_func_data_smooth.nii.gz
fslmaths prefiltered_func_data_smooth.nii.gz -mas ${func_dir}/${rest}_mask.nii.gz prefiltered_func_data_smooth.nii.gz

## 4. Grand mean Scaling
echo "Global intensity normalisation" 
fslmaths prefiltered_func_data_smooth.nii.gz -ing 10000 prefiltered_func_data_inn_volsorm.nii.gz
fslmaths prefiltered_func_data_inn_volsorm ${rest}_alff_pp.nii.gz
fslmaths ${rest}_alff_pp.nii.gz -Tmean mean_${rest}_alff_pp.nii.gz

## 5. clean up
echo "Clean temporal files"
rm -rf prefiltered_func_*.nii.gz


## CALCULATING ALFF AND fALFF
## 1. primary calculations
echo "there are ${n_vols} vols"
## decide whether n_vols is odd or even
MOD=`expr ${n_vols} % 2` ; echo "Odd (1) or Even (0): ${MOD}"
## if odd, remove the first volume
N=$(echo "scale=0; ${n_vols}/2"|bc) ; N=$(echo "2*${N}"|bc)  ; echo ${N}
echo "Deleting the first volume from bold data due to a bug in fslpspec"
if [ ${MOD} -eq 1 ]
then
    fslroi ${rest}_alff_pp.nii.gz prealff_func_data.nii.gz 1 ${N}
fi
if [ ${MOD} -eq 0 ]
then
    cp ${rest}_alff_pp.nii.gz prealff_func_data.nii.gz
fi

## 2. Computing power spectrum
echo "Computing power spectrum"
fslpspec prealff_func_data.nii.gz prealff_func_data_ps.nii.gz
## copy power spectrum to keep it for later (i.e. it does not get deleted in the clean up at the end of the script)
cp prealff_func_data_ps.nii.gz power_spectrum_distribution.nii.gz
echo "Computing square root of power spectrum"
fslmaths prealff_func_data_ps.nii.gz -sqrt prealff_func_data_ps_sqrt.nii.gz

## 3. Calculate ALFF
echo "Extracting power spectrum at the slow frequency band"
## calculate the low frequency point
n_lp=$(echo "scale=10; ${LP}*${N}*${TR}"|bc)
n1=$(echo "${n_lp}-1"|bc|xargs printf "%1.0f") ; 
echo "${LP} Hz is around the ${n1} frequency point."
## calculate the high frequency point
n_hp=$(echo "scale=10; ${HP}*${N}*${TR}"|bc)
n2=$(echo "${n_hp}-${n_lp}+1"|bc|xargs printf "%1.0f") ; 
echo "There are about ${n2} frequency points before ${HP} Hz."
## cut the low frequency data from the the whole frequency band
fslroi prealff_func_data_ps_sqrt.nii.gz prealff_func_ps_slow.nii.gz ${n1} ${n2}
## calculate ALFF as the sum of the amplitudes in the low frequency band
echo "Computing amplitude of the low frequency fluctuations (ALFF)"
fslmaths prealff_func_ps_slow.nii.gz -Tmean -mul ${n2} prealff_func_ps_alff4slow.nii.gz
cp prealff_func_ps_alff4slow.nii.gz ALFF.nii.gz

## 4. Calculate fALFF
echo "Computing amplitude of total frequency"
fslmaths prealff_func_data_ps_sqrt.nii.gz -Tmean -mul ${N} -div 2 prealff_func_ps_sum.nii.gz
## calculate fALFF as ALFF/amplitude of total frequency
echo "Computing fALFF"
fslmaths prealff_func_ps_alff4slow.nii.gz -div prealff_func_ps_sum.nii.gz fALFF.nii.gz

## 5. Z-normalisation across whole brain
echo "Normalizing ALFF/fALFF to Z-score across full brain"
fslstats ALFF.nii.gz -k ${func_dir}/${rest}_mask.nii.gz -m > mean_ALFF.txt ; mean=$( cat mean_ALFF.txt )
fslstats ALFF.nii.gz -k ${func_dir}/${rest}_mask.nii.gz -s > std_ALFF.txt ; std=$( cat std_ALFF.txt )
echo $mean $std
fslmaths ALFF.nii.gz -sub ${mean} -div ${std} -mas ${func_dir}/${rest}_mask.nii.gz ALFF_Z.nii.gz
fslstats fALFF.nii.gz -k ${func_dir}/${rest}_mask.nii.gz -m > mean_fALFF.txt ; mean=$( cat mean_fALFF.txt )
fslstats fALFF.nii.gz -k ${func_dir}/${rest}_mask.nii.gz -s > std_fALFF.txt ; std=$( cat std_fALFF.txt )
echo $mean $std
fslmaths fALFF.nii.gz -sub ${mean} -div ${std} -mas ${func_dir}/${rest}_mask.nii.gz fALFF_Z.nii.gz

## 6. Register Z-transformed ALFF and fALFF maps to standard space
echo Registering Z-transformed ALFF to standard space
flirt -in ${ALFF_dir}/ALFF_Z.nii.gz -ref ${standard} -applyxfm -init ${reg_dir}/example_func2standard.mat -out ${ALFF_dir}/ALFF_Z_2standard.nii.gz
echo Registering Z-transformed fALFF to standard space
flirt -in ${ALFF_dir}/fALFF_Z.nii.gz -ref ${standard} -applyxfm -init ${reg_dir}/example_func2standard.mat -out ${ALFF_dir}/fALFF_Z_2standard.nii.gz

## 7. Clean up
echo "Clean up temporary files"
rm -rf prealff_*.nii.gz

## END OF SUBJECT LOOP
done

cd ${cwd}