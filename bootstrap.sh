#!/bin/bash
cd ~
rm -rf sf-sample
git clone https://github.com/sirui-sun/sf-sample.git
cd ~/sf-sample
python3.7 publisher.py