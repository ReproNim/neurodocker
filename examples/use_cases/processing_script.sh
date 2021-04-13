#!/bin/bash

# This example assumes data located in directory
# called 'data' that has been mounted to '/home'
# (i.e. '/home/data')

input="/home/input"
output="/home/output"
cd ${input} || exit

#-----
# Brain extract with BET
#-----

echo "Running brain extraction..."
for subj in sub-*; do
    echo " > ${subj}"
    mkdir -p ${output}/${subj}
    bet ${input}/${subj}/${subj}_T1w.nii.gz ${output}/${subj}/${subj}_T1w_bet.nii.gz -m -R
done

#-----
# Warp to MNI using ANTS
#-----

echo "Warping to MNI..."
for subj in sub-*; do
    echo " > ${subj}"
    mkdir -p ${output}/${subj}
    antsRegistrationSyNQuick.sh \
        -d 3 \
        -f ${FSLDIR}/data/standard/MNI152_T1_1mm_brain.nii.gz \
        -m ${output}/${subj}/${subj}_T1w_bet.nii.gz \
        -o ${output}/${subj}/${subj}_T1w_bet2mni
done
