#!/bin/bash

file_path="output.csv"
prev_line_count=0
first_check=true

while true; do
  current_line_count=$(wc -l < "$file_path")

  if [ "$current_line_count" -gt "$prev_line_count" ]; then
    if [ "$first_check" = true ]; then
      first_check=false
    else
      echo ""
    fi
    echo -n "Line count: $current_line_count"
    prev_line_count="$current_line_count"
  else
    echo -n "."
  fi

  sleep 5
done
