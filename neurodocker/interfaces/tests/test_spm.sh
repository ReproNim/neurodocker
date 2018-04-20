#!/usr/bin/env bash

set -exu

echo 'fprintf("testing")' > /tmp/test.m
$SPMMCRCMD /tmp/test.m

printf 'passed'
