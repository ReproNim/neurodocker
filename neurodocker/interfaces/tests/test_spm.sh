#!/usr/bin/env bash

set -e
set -x

echo 'fprintf("testing")' > /tmp/test.m
$SPMMCRCMD /tmp/test.m
