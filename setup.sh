#!/bin/bash
pip3 install selenium
xattr -d com.apple.quarantine chromedriver
spctl --add --label 'Approved' chromedriver