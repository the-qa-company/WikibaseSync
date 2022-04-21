while true  
do  
  pkill -f import_recent_changes.py &
  python import_recent_changes.py &
  sleep 300  
done
