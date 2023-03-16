#!/bin/bash

kli init --name kassh --salt 0ACDEyMzQ1Njc4OWxtbm9dEf --nopasscode --config-dir ${KASSH_SCRIPT_DIR} --config-file demo-witness-oobis
kli incept --name kassh --alias kassh --file ${KASSH_SCRIPT_DIR}/incept.json

kli oobi resolve --name kassh --oobi-alias schema --oobi http://192.168.86.207:7723/oobi/EKgMCHV98k4xz2rJnt2x556pGBCUfA6n5x03mvQv5tPo

kassh server start --name kassh --alias kassh
