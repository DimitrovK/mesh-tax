#!/bin/bash
# bench.sh <label>  -- runs fortio against 1-hop and 2-hop targets
set -u
export PATH=$HOME/.local/bin:$PATH
L="$1"; mkdir -p out/$L
POD=$(kubectl get pod -l app=loadgen -o jsonpath='{.items[0].metadata.name}')
for target in "backend:8080 one_hop" "frontend:8080 two_hop"; do
  set -- $target; URL=$1; NAME=$2
  for c in 1 8 32; do
    echo "  $L $NAME c=$c"
    kubectl exec "$POD" -c fortio -- fortio load -c $c -qps 0 -t 25s -a -json - \
      "http://$URL/" > "out/$L/${NAME}_c${c}.json" 2>/dev/null
  done
done
