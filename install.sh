if [ $# -lt 1 ]; then
  echo "Error: Provide argument for minute time interval: bash install.sh NUMBER_OF_MINUTES"
  exit 1
fi

# create cron file
CRON_FILE="/var/spool/cron/root"
sudo touch $CRON_FILE
sudo /usr/bin/crontab $CRON_FILE

#register cron job
sudo crontab -l > cron_bkp
#sudo echo "*/$1 * * * * sudo flock -x $(pwd)/cron.lock -c \"$(which echo) 'cron works' >> $(pwd)/cron.txt\" " > cron_bkp
sudo echo "*/$1 * * * * sudo flock -x $(pwd)/cron.lock -c \"$(which python) $(pwd)/run.py\"" > cron_bkp
sudo crontab cron_bkp
sudo rm cron_bkp
sudo service cron start