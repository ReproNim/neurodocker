#!/opt/miniconda-latest/envs/analysis/bin/python3

import subprocess
import os
from pathlib import Path
from glob import glob
# Importing these for example, eventhough not used here
import pandas as pd
import numpy as np
import nibabel as nb

# This example assumes data located in directory
# called 'data' that has been mounted to '/home'
# (i.e. '/home/data')

input = Path("/home/input")
output = Path("/home/output")
os.chdir(input)


def runBash(cmd):
    subprocess.check_call(cmd, shell=True)


#-----
# Brain extract with BET
#-----

print("Running brain extraction...")
for subj in glob("sub-*"):
    print(f" > {subj}")
    Path(f"{output}/{subj}").mkdir(parents=True, exist_ok=True)
    bet_cmd = f"bet {input}/{subj}/{subj}_T1w.nii.gz {output}/{subj}/{subj}_T1w_bet.nii.gz -m -R"
    runBash(bet_cmd)

#-----
# Warp to MNI using ANTS
#-----

print("Running brain extraction...")
for subj in glob("sub-*"):
    print(f" > {subj}")
    Path(f"{output}/{subj}").mkdir(parents=True, exist_ok=True)
    ants_cmd = f"""
    antsRegistrationSyNQuick.sh \
        -d 3 \
        -f $FSLDIR/data/standard/MNI152_T1_1mm_brain.nii.gz \
        -m {output}/{subj}/{subj}_T1w_bet.nii.gz \
        -o {output}/{subj}/{subj}_T1w_bet2mni
        """
    runBash(ants_cmd)
