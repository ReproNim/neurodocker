#!/usr/bin/env bash

set -ex

echo 'fprintf("testing")' > /tmp/test.m
$SPMMCRCMD /tmp/test.m

printf 'passed'
