# Read Password
read -s -p "MySQL Password: " password
# Run Command
perl -pi -e "s/csqsiew/root/g" ./config.json
perl -pi -e "s/u98x7v89asx/$password/g" ./config.json