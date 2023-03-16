#!/bin/bash

kli init --name issuer --salt 0ACDEyMzQ1Njc4OWxtbm9aBc --nopasscode --config-dir ${KASSH_SCRIPT_DIR} --config-file demo-witness-oobis
kli incept --name issuer --alias issuer --file ${KASSH_SCRIPT_DIR}/incept.json

kli init --name holder --salt 0ACDEyMzQ1Njc4OWxtbm9qWc --nopasscode --config-dir ${KASSH_SCRIPT_DIR} --config-file demo-witness-oobis
kli incept --name holder --alias holder --file ${KASSH_SCRIPT_DIR}/incept.json

kli oobi resolve --name issuer --oobi-alias holder --oobi http://127.0.0.1:5642/oobi/EAa46iafkH0lpUkn7YGZ3kdvC9nNUiImhLNlODiw86AI/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
kli oobi resolve --name holder --oobi-alias issuer --oobi http://127.0.0.1:5642/oobi/EImOExnAuY3_6C2J48HhGytUDAvQEB2Ypy6pLs0GxfBR/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
kli oobi resolve --name issuer --oobi-alias issuer --oobi http://127.0.0.1:7723/oobi/EKgMCHV98k4xz2rJnt2x556pGBCUfA6n5x03mvQv5tPo
kli oobi resolve --name holder --oobi-alias holder --oobi http://127.0.0.1:7723/oobi/EKgMCHV98k4xz2rJnt2x556pGBCUfA6n5x03mvQv5tPo

kli vc registry incept --name issuer --alias issuer --registry-name vLEI

kli vc issue --name issuer --alias issuer --registry-name vLEI --schema EKgMCHV98k4xz2rJnt2x556pGBCUfA6n5x03mvQv5tPo --recipient EAa46iafkH0lpUkn7YGZ3kdvC9nNUiImhLNlODiw86AI --data @${KASSH_SCRIPT_DIR}/auth-data.json
sleep 2
kli vc list --name holder --alias holder --poll

echo 'kli oobi resolve --name holder --oobi-alias kassh --oobi http://127.0.0.1:9723/oobi'
