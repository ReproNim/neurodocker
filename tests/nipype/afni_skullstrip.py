# vi: set ft=python sts=4 ts=4 sw=4 et:
from __future__ import absolute_import
import os
import argparse

from bids.grabbids import BIDSLayout
from nipype import Node
from nipype.interfaces import afni

# does this even work?
from utils import base_version, env_to_json

# setup environment tracker
ENV = base_version()
# make this more dynamic
OUTDIR = '/data/afni'


def create_workflow():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='data',
                        help="path to bids dataset")
    args = parser.parse_args()
    if not os.path.exists(args.data):
        raise IOError('data not found')
    if not os.path.exists(OUTDIR):
        os.makedirs(OUTDIR)

    # grab data from bids structure
    layout = BIDSLayout(args.data)
    subj = layout.get_subjects()[0]
    t1 = [f.filename for f in layout.get(subject=subj, type='T1w',
                                         extensions=['nii.gz'])][0]

    outfile = os.path.join(OUTDIR, 'test_{}_{}'.format(subj, ENV['os']))

    # run afni skullstrip
    skullstrip = afni.SkullStrip()
    skullstrip.inputs.in_file = t1
    skullstrip.inputs.outputtype = 'NIFTI_GZ'
    # FIX: this has to be unique for each environment
    skullstrip.inputs.out_file = outfile + '.nii.gz'
    res = skullstrip.run()
    # write out json to keep track of information
    ENV.update({'inputs': res.inputs})
    #ENV.update({'outputs': res.outputs})
    # write out to json
    env_to_json(ENV, outname=outfile + '.json')

if __name__ == '__main__':
    create_workflow()
