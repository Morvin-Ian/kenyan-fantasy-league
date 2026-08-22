#!/bin/bash
set -o errexit
set -o nounset

exec celery -A config worker --loglevel=info
