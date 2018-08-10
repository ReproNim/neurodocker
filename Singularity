Bootstrap: docker
From: alpine:3.7


%post
mkdir /opt
cd /opt
tmp_pkgs="curl gcc musl-dev python3-dev sqlite-dev git" 
apk add --update --no-cache git python3 py3-yaml rsync $tmp_pkgs 
git clone  https://github.com/kaczmarj/neurodocker.git
curl -fsSL https://bootstrap.pypa.io/get-pip.py | python3 - 
pip install --no-cache-dir reprozip 
#apk del $tmp_pkgs 
#rm -rf /var/cache/apk/* ~/.cache/pip/*

pip install --no-cache-dir -e /opt/neurodocker 
#neurodocker --help

%runscript
neurodocker