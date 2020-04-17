#!/bin/sh
i=0

for f in reddit_urls/batch_1/*.txt; do
    
    python3 reddit_crawler.py --url $f --output "/gpfs/gpfsfpo/reddit_dataset/batch1/${i}/" &
  
    i=$((i+1))
    echo $i
    echo $f

    if [ $i -ge 50 ] 
    then
      i=0   
      wait $!
    fi

done 2>/dev/null

trap '
  trap - INT # restore default INT handler
  kill -s INT "$$"
' INT
