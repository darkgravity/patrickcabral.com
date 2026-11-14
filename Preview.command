#!/bin/zsh
project_dir="${0:A:h}"
python3 "$project_dir/scripts/preview.py"
if [ $? -ne 0 ]; then
  printf '\nPreview could not start. Press Return to close this window.\n'
  read -r
fi
