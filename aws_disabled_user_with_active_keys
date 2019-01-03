#!/bin/bash
#
# by github.com/Lucas-L-Alcantara
#.
#..
#...
# This script will print a list of disabled aws accounts with active secret key

[ -e 2-disable.csv ] && rm 2-disable.csv

# Exporting list of aws user accounts
aws iam generate-credential-report

for i in $n_procs; do
    ./procs[${i}] &
    pids[${i}]=$!
done

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done

aws iam get-credential-report >> users-aws.csv


#Clear file:
sed -i '$d' users-aws.csv
sed -i '$d' users-aws.csv
encoded=$(grep -n "Content" users-aws.csv | sed "s/..$//" |awk '{gsub("\"","");print $3}')
echo "$encoded" >> encoded.txt

#Converting to base64
rm users-aws.csv
decoded=$(base64 -d < encoded.txt)
echo "$decoded" >> users-aws.csv
rm encoded.txt


#Print Header

echo "AWS disabled accounts with active keys:" > 2-disable.csv
echo "---------------------------------------" >> 2-disable.csv
echo "NAME,LAST USE" >> 2-disable.csv
#Filtering by disabled accounts with active keys
cat users-aws.csv | awk -F, '$4 ~ /false/' | awk -F, '$9 ~ /true/ {print $1","$10}' >> 2-disable.csv
cat users-aws.csv | awk -F, '$4 ~ /false/' | awk -F, '$14 ~ /true/ {print $1","$15}' >> 2-disable.csv


#Delete temp file
[ -e users-aws.csv ] && rm users-aws.csv

#Done
cat 2-disable.csv | column -t -s,
