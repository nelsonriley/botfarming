while true
do
    kill $LASTPID
    python binance_update_order_book.py&     # <-- Note '&' to run in background
    LASTPID=$!               # Save $! in case you do other background-y stuff
    sleep 20;
    kill $LASTPID0
    kill $LASTPID1
    kill $LASTPID2
    kill $LASTPID3
    kill $LASTPID4
    python binance_update_order_book_0.py&     # <-- Note '&' to run in background
    LASTPID0=$!               # Save $! in case you do other background-y stuff
    python binance_update_order_book_1.py&     # <-- Note '&' to run in background
    LASTPID1=$!               # Save $! in case you do other background-y stuff
    python binance_update_order_book_2.py&     # <-- Note '&' to run in background
    LASTPID2=$!               # Save $! in case you do other background-y stuff
    python binance_update_order_book_3.py&     # <-- Note '&' to run in background
    LASTPID3=$!               # Save $! in case you do other background-y stuff
    python binance_update_order_book_4.py&     # <-- Note '&' to run in background
    LASTPID4=$!               # Save $! in case you do other background-y stuff
    
    sleep 3600;   # Sleep then kill to set timeout.
    

done