#!/bin/sh

#grep -H '' log/*data.log 					> 5_decode.txt
grep -H fd_redis_writer log/*data.log 				> 5_decode_req.txt
grep -H fd_redis_reader log/*data.log 				> 5_decode_ack.txt

grep -H imagecode.aspx 	log/*time.log 	| grep IMAGE_CONTENT	> 5_image_get.txt
grep -H bid.aspx 	log/*time.log 	| grep BIDAMOUNT 	> 5_price_get.txt

grep -H 'login' log/*warning.log 	| grep -v 'failed' 	> 5_login.txt
grep -H 'bids finished' log/*warning.log 			> 5_result.txt

