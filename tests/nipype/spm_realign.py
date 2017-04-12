from __future__ import absolute_import
import os
import argparse

from bids.grabbids import BIDSLayout
from nipype import Node
from nipype.interfaces.spm import Realign

from .utils import base_version, env_to_json

# setup environment tracker
ENV = base_version()
# make this more dynamic
OUTDIR = '/data/spm'

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
    func = [f.filename for f in layout.get(subject=subj, type='bold',
                                           extensions=['nii.gz'])][0]

    outfile = os.path.join(OUTDIR, 'test_{}_{}'.format(subj, ENV['os']))

    # run interface
    realign = Realign()
    realign.inputs.in_files = func
    # FIX: this has to be unique for each environment
    realign.inputs.out_prefix = outfile
    res = mcflirt.run()

    # write out json to keep track of information
    ENV.update({'inputs': res.inputs})
    ENV.update({'nipype_version': nipype.__version__})
    #ENV.update({'outputs': res.outputs})
    # write out to json
    env_to_json(ENV, outname=outfile + '.json')

if __name__ == '__main__':
    create_workflow()
