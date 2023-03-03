#!/bin/sh

# Help function
help()
{
   # Display help
   echo "Check if Telegram bot is running, start it if necessary."
   echo
   echo "Syntax: /bin/bash telegram_health_check.sh [-h] path_to_logs"
   echo "Args:"
   echo "path_to_logs   Absolute path to logs directory."
   echo "Options:"
   echo "h     Print help."
   echo
}

# Process the input options.
# Get the options
while getopts ":h" option; do
   case $option in
      h) # display help
         help
         exit;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

eval "$(conda shell.bash hook)"
conda activate moviebot

# Log files
now=$(date +"%d%m%Y-%H%M")
path=$1
telegram_logs="${path}/telegram-${now}.log"

if ! ps ax | grep -v grep | grep "moviebot.run"
then
    python -m moviebot.run > "$telegram_logs" 2>&1 &
fi

conda deactivate
