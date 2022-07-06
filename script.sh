while true  
do
  echo "kill previews process"
  pkill -f import_recent_changes.py
  sleep 3
  echo "importing entity"
  python -u import_recent_changes.py &
  echo "import done"
  sleep 300
done
