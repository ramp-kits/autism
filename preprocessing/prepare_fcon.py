#!/usr/bin/env python3
"""
ntraut 2017
order files for fcon scripts
"""

# pylint: disable=C0103
import os
from glob import glob
import subprocess

# intitial data structure (to be adapted)
idir = "XXX" # Path to input dataset
siteTemplate = "*"
sessionTemplate = "ses*"
functionalTemplate = "func/*_task-rest_*bold.nii.gz"
anatomicalTemplate = "anat/*_T1w.nii.gz"

# output directory
odir = "$HOME/abide2/data/fcon"

print("Generating file structure...")
site_dirs = sorted(glob(os.path.join(idir, siteTemplate)))
params = {}
for site_dir in site_dirs:
    site_id = os.path.basename(site_dir)
    print(site_id)
    site_path = os.path.join(odir, site_id)
    params[site_id] = []
    subject_dirs = sorted(glob(os.path.join(site_dir, "*")))
    for subject_dir in subject_dirs:
        subject_id = os.path.basename(subject_dir)
        subject_path = os.path.join(site_path, subject_id)
        session_dirs = sorted(glob(os.path.join(subject_dir, sessionTemplate)))
        session_index = 0
        for session_dir in session_dirs:
            # Give a priority to images without acquisition label
            functional_MRIs = sorted(glob(os.path.join(session_dir, functionalTemplate)),
                                     key=lambda x: x.replace("_run", "1run"))
            anatomical_MRIs = sorted(glob(os.path.join(session_dir, anatomicalTemplate)),
                                     key=lambda x: x.replace("_run", "1run"))
            if not functional_MRIs or not anatomical_MRIs:
                continue
            for run_index, functional_MRI in enumerate(functional_MRIs):
                session_path = os.path.join(subject_path, "run_" + str(run_index + 1), "session_" +
                                            str(session_index + 1))
                functional_path = os.path.join(session_path, "rest_1")
                os.makedirs(functional_path, exist_ok=True)
                ofile = os.path.join(functional_path, "rest.nii.gz")
                if not os.path.isfile(ofile):
                    subprocess.call(["fslchfiletype", "NIFTI_GZ", functional_MRI, ofile])
                    # os.link(functional_MRI, ofile)

                # add to batch list only for session 1
                if session_index == 0:
                    output = subprocess.check_output("fslinfo " + ofile, shell=True).decode()
                    infos = dict(item.split() for item in output.splitlines())
                    dim4 = int(infos['dim4'])
                    pixdim4 = float(infos['pixdim4'])
                    subject_string = os.path.join(subject_id, "run_" + str(run_index + 1))
                    found = False
                    for param in params[site_id]:
                        if param['dim4'] == dim4 and param['pixdim4'] == pixdim4:
                            param['subjects'].append(subject_string)
                            found = True
                            break
                    if not found:
                        params[site_id].append({'dim4': dim4, 'pixdim4': pixdim4,
                                                'subjects': [subject_string]})

                for anatomical_index, anatomical_MRI in enumerate(anatomical_MRIs):
                    anatomical_path = os.path.join(session_path, "anat_" +
                                                   str(anatomical_index + 1))
                    os.makedirs(anatomical_path, exist_ok=True)
                    ofile = os.path.join(anatomical_path, "anat.nii.gz")
                    if not os.path.isfile(ofile):
                        subprocess.call(["fslchfiletype", "NIFTI_GZ", anatomical_MRI, ofile])
                        # os.link(anatomical_MRI, ofile)
            session_index += 1

print("Writing batch list...")
step = 20
with open(os.path.join(odir, "batch_list.txt"), "w") as batch_list:
    for site in params:
        index = 0
        for param in params[site]:
            site_path = os.path.join(odir, site)
            dim4 = param['dim4']
            pixdim4 = param['pixdim4']
            subjects = param['subjects']
            for x in range(0, len(subjects), step):
                subjects_file = os.path.join(site_path, "subjects-{}.txt".format(index + 1))
                index += 1
                with open(subjects_file, "w") as f:
                    for line in subjects[x:x+step]:
                        print(line, file=f)
                print(site_path, subjects_file, 0, dim4-1, dim4, pixdim4, file=batch_list)
