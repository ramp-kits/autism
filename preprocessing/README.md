# MRI preprocessing

## Files structure
Anatomical and functional MRI has to be in nifti format and in a specific
folder organization to be recognized by the fcon_1000 scripts.
The script `prepare_fcon.py` can be used to organize folders.

## Anatomical preprocessing
Anatomical MRI were segmented with FreeSufer 6.0.0 using the command:
```
recon-all -subjid $subjid -i $subjanat -autorecon-all
```
We extracted volumes, areas and cortical thicknesses with the script
`freesurfer/extract-stats.sh`


## fMRI preprocessing

### F1000 scripts

The preprocessing pipeline used for the resting-state fMRI data can be found in
the folder `scripts_f1000`. One can refer to the file
`scripts_f1000/batch_process` in which the parameters used for the
preprocessing are defined. The preprocessing pipeline is defined in the file
`scripts_f1000/0_preprocess.sh`. The preprocessing pipeline is composed of:

1. Anatomical scan preprocessing: deobliquing, reorienting, and skull
   stripping;
2. Function scan preprocessing: dropping first TRs, debobliquing, reorienting,
   motion correction, skull stripping, spatial smooting, grand-mean scaling,
   band-pass filtering, removing linear and quadratic tends, mask generation of
   preprocessed;
3. Registration: register functional to T1, registration T1 to standard,
   registration of functional to standard;
4. Segmentation: brain, CSF, and WM segmentation;
5. Nuisance signal regression.

The original scripts are available at:
www.nitrc.org/projects/fcon_1000

### Time-series extraction

The script `extract_time_series.py` was used to extract the time-series from
the preprocessed fMRI data.

