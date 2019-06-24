# python-piperci
[![Build Status](https://travis-ci.com/AFCYBER-DREAM/python-piperci.svg?branch=master)](https://travis-ci.com/AFCYBER-DREAM/python-piperci)

Python library for common piperci functions


## SRI CLI Tools

Manually generate SRI Hashes with
`echo "sha256-$(openssl dgst -binary -sha256 README.md | openssl base64 -A)"`

This tool eases some of the additional tasks around SRI hashes
```
sritool generate README.md
sha256-8Kp2VF7e9rvFyGmgLFPD8v7Xk7fCVr80Vbtz5am1L3E=

sritool --url-safe generate README.md
c2hhMjU2LThLcDJWRjdlOXJ2RnlHbWdMRlBEOHY3WGs3ZkNWcjgwVmJ0ejVhbTFMM0U9

sritool decode c2hhMjU2LThLcDJWRjdlOXJ2RnlHbWdMRlBEOHY3WGs3ZkNWcjgwVmJ0ejVhbTFMM0U9
sha256-8Kp2VF7e9rvFyGmgLFPD8v7Xk7fCVr80Vbtz5am1L3E=

sritool --url-safe verify README.md c2hhMjU2LThLcDJWRjdlOXJ2RnlHbWdMRlBEOHY3WGs3ZkNWcjgwVmJ0ejVhbTFMM0U9

3WGs3ZkNWcjgwVmJ0ejVhbTFMM0U9
sha256-8Kp2VF7e9rvFyGmgLFPD8v7Xk7fCVr80Vbtz5am1L3E=
urlsafeb64: c2hhMjU2LThLcDJWRjdlOXJ2RnlHbWdMRlBEOHY3WGs3ZkNWcjgwVmJ0ejVhbTFMM0U9
```
