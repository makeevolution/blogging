#!/bin/bash
. venv/bin/activate
while true; do
    flask deploy
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done
# --access-logfile and --error-logfile ensures all access and error logfiles
# to be written to stdout, instead of the default which is to write to a log file
# (defaulted by Docker)
exec gunicorn -b :5000 --access-logfile - --error-logfile - flasky:app
