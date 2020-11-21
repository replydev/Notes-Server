sudo apt-get update
sudo apt-get install python3
sudo apt-get install python3-pip
sudo apt-get install mariadb-server
sudo apt-get install libmariadb3
sudo apt-get install libmariadb-dev
sudo apt-get install apt-transport-https
curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | sudo bash
sudo apt-get update
sudo apt-get install libmariadb3
pip3 install -r requirements.txt