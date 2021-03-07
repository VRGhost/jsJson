#!/bin/bash -e

source "$(dirname "${BASH_SOURCE[0]}")/env.sh"

DEV_ENV_NAME='py-js-json-dev'
init_venv "${DEV_ENV_NAME}"

maybe_run_pip_install "${DEV_ENV_NAME}" "${REQUIREMENTS_DIR}/development.txt"
exec bash --rcfile <(echo '. ~/.bashrc;' "cd '${PROJ_ROOT}' ; . '$(get_venv_root "${DEV_ENV_NAME}")/bin/activate'")