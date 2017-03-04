# vi: set ft=python sts=4 ts=4 sw=4 et:
import os
import argparse

from bids.grabbids import BIDSLayout

from nipype import Node, DataGrabber, IdentityInterface
from nipype.interfaces import afni

def create_workflow():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='data', 
                        help="path to bids dataset")
    args = parser.parse_args()
    if not os.path.exists(args.data):
        raise IOError('data not found')

    layout = BIDSLayout(args.data)

    # grab data from bids structure
    subj = layout.get_subjects()[0]
    t1 = [f.filename for f in layout.get(subject=subj, type='T1w', extensions=['nii.gz'])][0]
    # run afni skullstrip
    skullstrip = afni.SkullStrip()
    skullstrip.inputs.in_file = t1
    skullstrip.inputs.outputtype = 'NIFTI_GZ'
    skullstrip.inputs.out_file = 'test_case.nii.gz'
    res = skullstrip.run()

if __name__ == '__main__':
    create_workflow()
