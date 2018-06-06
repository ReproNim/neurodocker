#!/usr/bin/env bash
#
# Run the neurodocker examples and check for failures.

set -eu

here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Test examples/README.md
sed -e ':a' -e 'N' -e '$!ba' -e 's/\\\n/ /g' ${here}/README.md \
| grep 'neurodocker generate' \
| while read c; do eval $c; done


# Test specialized examples.
find $here -name generate.sh | while read c; do bash $c; done
