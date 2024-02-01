#!/bin/bash

scripts=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export KASSH_SCRIPT_DIR="${scripts}"
