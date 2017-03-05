import platform
import sys
import json

def check_os():
    info = platform.uname()
    return {'os': '{}-{}'.format(info.system, info.release)}

def check_py_vers():
    return {'python': '.'.join([str(x) for x in sys.version_info[:3]])}

def base_version():
    master = {}
    master.update(check_os())
    master.update(check_py_vers())
    return master

def env_to_json(info, outname="environment-info.json"):
    with open(outname, 'w') as fp:
        json.dump(info, fp, sort_keys=True, indent=4)
