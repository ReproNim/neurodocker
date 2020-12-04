#!/usr/bin/env bash

set -exu

echo "a = 1" > ~/test.m
$SPMMCRCMD ~/test.m

printf 'passed'
echo
