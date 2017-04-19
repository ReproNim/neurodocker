from __future__ import absolute_import

from neurodocker.interfaces import ANTs, FSL, SPM


SUPPORTED_NI_SOFTWARE = {'ants': ANTs,
                         'fsl': FSL,
                         'spm': SPM,
                         }
