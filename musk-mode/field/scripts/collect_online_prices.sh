#!/bin/bash
# Weekly price tracker: real listed prices for the tracer basket from a Lagos online pharmacy.
# Usage: bash collect_online_prices.sh <empty_raw_dir> <out.csv>
# Polite: one request every 2 seconds. Listed online prices are NOT street/PPMV prices; use them only as a weekly index.
set -e
RAW=$1; OUT=$2; mkdir -p "$RAW"
for q in artemether lumefantrine coartem lonart amatem amlodipine lisinopril losartan nifedipine metformin glibenclamide amoxicillin "malaria test" ciprofloxacin ORS zinc; do
  qq=$(echo "$q" | sed 's/ /+/g')
  curl -sS -L -A "Mozilla/5.0 (price research)" --max-time 25 -o "$RAW/medplusnig__${qq}.html" "https://medplusnig.com/products?name=$qq&data_from=search&page=1"
  sleep 2
done
python3 -I "$(dirname "$0")/parse_online_prices.py" "$RAW" "$OUT"
