#!/bin/bash

# Safety settings
set -e

# Check if we have a script path
if [ $# -ne 1 ]; then
    echo "{\"error\": \"Usage: $0 <script_path>\"}"
    exit 1
fi

SCRIPT_PATH="$1"

# Check if we're running in Cloud Run (simplified check based on environment)
if [ -f "/.dockerenv" ] && [ -d "/var/run/secrets/kubernetes.io" ]; then
    # We're likely in Cloud Run - use direct execution
    python3 /app/executor.py "$SCRIPT_PATH"
else
    # We're likely running locally - use NSJail
    /usr/local/bin/nsjail \
        --quiet \
        --mode once \
        --time_limit 5 \
        --bindmount /tmp:/tmp:rw \
        --bindmount /app:/app:ro \
        --bindmount /usr:/usr:ro \
        --bindmount /lib:/lib:ro \
        --bindmount /lib64:/lib64:ro \
        --bindmount /etc:/etc:ro \
        --bindmount /dev/urandom:/dev/urandom:ro \
        --bindmount /bin:/bin:ro \
        --bindmount /sbin:/sbin:ro \
        --cwd /tmp \
        --rlimit_as 1024 \
        --rlimit_cpu 5 \
        --rlimit_fsize 1024 \
        --rlimit_nofile 32 \
        --disable_clone_newnet \
        --disable_clone_newuser \
        --disable_clone_newns \
        --disable_clone_newpid \
        --disable_clone_newipc \
        --disable_clone_newuts \
        --disable_clone_newcgroup \
        -- /usr/bin/python3 /app/executor.py "$SCRIPT_PATH"
fi