#!/bin/sh

grep -H fd_redis_writer log/*data.log |grep -v ' 11:'		> 1_decode_req.txt
grep -H fd_redis_reader log/*data.log |grep -v ' 11:'		> 1_decode_ack.txt

grep -H fd_redis_writer log/*data.log |grep ' 11:'		> 2_decode_req.txt
grep -H fd_redis_reader log/*data.log |grep ' 11:'		> 2_decode_ack.txt

grep -H imagecode.aspx 	log/*time.log 	|grep IMAGE_CONTENT 	|grep -v ' 11:'	> 1_image_get.txt
grep -H bid.aspx 	log/*time.log 	|grep BIDAMOUNT  	|grep -v ' 11:'	> 1_price_get.txt

grep -H imagecode.aspx 	log/*time.log 	|grep IMAGE_CONTENT 	|grep ' 11:'	> 2_image_get.txt
grep -H bid.aspx 	log/*time.log 	|grep BIDAMOUNT  	|grep ' 11:'	> 2_price_get.txt

grep -H imagecode.aspx 	log/*info.log 	|grep -v ' 11:'		> 1_image_req.txt
grep -H bid.aspx 	log/*info.log 	|grep -v ' 11:'		> 1_price_req.txt

grep -H imagecode.aspx 	log/*info.log 	|grep ' 11:'		> 2_image_req.txt
grep -H bid.aspx 	log/*info.log 	|grep ' 11:'		> 2_price_req.txt


grep -H 'login' log/*warning.log 	|grep -v 'failed' 	> 0_login.txt
grep -H 'bid 0 price 73700' log/*warning.log 			> 0_bidok.txt
grep -H 'bids finished' log/*warning.log 			> 0_result.txt
grep -H -E '<ERRORCODE>112</ERRORCODE>' log/*time*		> 0_bid112.txt


