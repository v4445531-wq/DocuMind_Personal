#!/bin/sh
# Start gateway on port 8081 (nginx proxies /api/ to it)
uvicorn app.main:app --host 0.0.0.0 --port 8081 &
# Start nginx on port 8080 (serves frontend + proxies API)
nginx -g 'daemon off;'
