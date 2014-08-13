
#include <stdio.h>
#include <string.h>

#include "hiredis.h"

#include "fd_redis.h"

/*
   char test_image[] = "/zZ/u00GIaP9HW010G000G01003/sm1302WS7YCU6IWZ8ICjAoWmF6H1F3StF7jONKbaaO2Pbe+0Z8gWjER3eAhQhOgCoF/Bskxr////cy7////w/+Rz//Z/sm130IijBJmrF7P1GNRufOob+FZu+FZu+FZu+FZu+FZu+FZu+FZu+FZu+FZu+FZu+FZu+FZu+FZu+FZu+FZu+FZu+FZ/m00H200X07430I800X410n41/yG07m000GK10G410G400000000000420mG51WS82GeB/yG0jH000W430m840mK510G0005z0G8300GH1H8XCK464r5X1o9n53A1aQ488qAnmHLIqV0aCs9oWWaA5XSO6Heb9YSeAIeqDJOtE3awGqH5HaT8IKfJL5LMLrXPMcDaPMPdQ6bgStHrTdTuUNg3X8M6XuY9YfAJb9MMbvYPcgAZfAMcfwYfghApjBMsjxYvkiB3nCN6nyZ9ojBJrDNMrzZPsk7Yu+JbvkVewUhnylFqzVRt+Fdw/yG07m400m410G410G410G00000000420mG51WS82GeB/yG0jH400W4210G310S510G00G9t00420n441I4n1X91KGTXSHCYCe4854AHeR712ICpKl0LOdBH2XOaDE4byHSO6Hec9oWfAZKsDpWvEaD4HKP7I4bAKrHLLbTOMLfZP6LcPsXfQdDqTNPtU7bwWeE4XOQ7Y8cAafEKbPQNc9cQegEafQQdgAcgihEqjRQtkBcwmiF4nSR7oCdAqjFKrTRNsDdQukFavURdwEdgylFqzVRt+Fdw/ze030C1008H0n40Fm2vQMjlzaXPe8cp6f9A0dEAb+oMozRUB7+uEABFvRA3FJor/3YadlRUqa4Sict8o1j9mAP0lsIsNhRnO/t1nGrhQe2pGGxUf9GSV/Mg9TKizmLPivu02D/XLMzqoMIwCtdhvMC4l/0E+EsFy+z0ouaDanEs29XZT/gnm2JpqwS7/m3LHB3Pswxf88GfE1+x1EVGSSrYwEN5+kqaAGTv0pn/+l5Qm96et1PDxH832fEE2ESVZncWDXohOcK9v20jaWF3j+kCZcfJQsg0irl3jwab1n/zQgRIoosCxNCMm80qROAaDZi3pmUCrIkvpCKYa1tXG27+N3O7Jqvp/ZqnKOyp0qN+nneidsH36pbIVB70mJk778upJc/iwDa1It8VeGeFw+bLRWxjB4Yi2ft31noIsSvuzCu7jJD5O2uOCM94V7e1ddzVwqEEcWrRTcajjQ4RbXWP3t20qnuxAEJOOOYUf2nxYlrmAhMyosxpN7aVkvC+MoZZ0xUsJKqEBAmyuBlB0Cnw4v//05rArASR4YHMJCLM6B8wgOm2Fm8wK/x9RBrjuiVxWug2wnv4LuguPDhO1vmUsVJchttFzt+LDebgsfnj555ICwkp+MoWpqyjVmughSAqUghAi4aeM72Ou0R9wdeEC/dLgp+MoWpqyjVmufiaqrlSVD4NjYE6HSbJxyzFmfaZFjhmIejr1vCRyA+/S0VG+d+UrGwhTGm1O98ZAh3SLtbSUdJh/m3MfBuFV5BUEEH8msvf7Gg0CTizUly0aLVbG52De8781w3sw7WzFne3OeQTVmD8BUA3ob8pr7N0/Fl+NvFjJiDxS+NlaMHb6Ek0E1LoE6E1cCQAYjZ8LGCVvpK4bj95TVQRTm2m0T6+wt+7+VUWH7QJ6zYbZdH6YmlAZZaP8/2i4nkiQEoaAuEq+kEAwAU6udJotP8OJzxOnOaUdGO7+UbIoMi3HB7966ZKO6Ug/ZrgeIvMFOe6GDf6p6/8+wSzpnWvvmIFNqFNYlPmohRNCgA7B9j7odeUkFy0FKVdf3JhP2FbOnWxjXObGUESVvw/a/ofBTimRJ4Jaet0Nw7iFQXliKdP4KOTDDbHasggigd6CZ7N7RDH0IFec06SdyICDLfuvfFabAf3/4g4adspnWKaSCbgI8Y7X9o5SaRFnvuf8ToAv1NIbGvoLKOFNF75NlkVxly0AgnWTvbadO2D3bOrEG3warP+v/k/oePBPnj555ICAAAA02YYYW0eeee0AAAA02YYYW0eeee0AAAA02YYYW3/sG";

   char test_sid[] = "9E547C5BF6FF532C8F0A6093BAF6D7A2";
   */


char server_ip[] = "192.168.1.90";
int  server_port = 6379;
char password[]  = "river";
int  redis_dbid  = 5;

char req_key[] = "req_image";
char ack_key[] = "ack_number";

//=====================================================================================

redisContext *redis_connect;

int redis_init(void)
{
	//struct timeval timeout = { 2, 500000 }; // 2.5 seconds
	//redis_connect = redisConnectWithTimeout((char*)server_ip, server_port, timeout);

	redis_connect = redisConnect((char*)server_ip, server_port);
	if (redis_connect->err) {
		printf("Connection error: %s\n", redis_connect->errstr);
		redisFree(redis_connect);
		return -1;
	}

	redisReply *reply = NULL;
	reply= redisCommand(redis_connect, "AUTH %s", password);
	if (reply->type == REDIS_REPLY_ERROR) {
		printf("Password error: %s\n", password);
		freeReplyObject(reply);
		redisFree(redis_connect);
		return -1;
	}
	freeReplyObject(reply);

	reply = redisCommand(redis_connect, "SELECT %d", redis_dbid);
	freeReplyObject(reply);

	return 0;
}

int redis_clean(void)
{
	redisFree(redis_connect);
	return 0;
}

int redis_get(char* buff)
{
	redisReply *reply = NULL;
	reply = redisCommand(redis_connect, "LPOP %s", req_key);
	//reply = redisCommand(redis_connect, "BLPOP req_image 0");
	if (reply == NULL || reply->type == REDIS_REPLY_ERROR) {
		buff[0] = 0;
		printf("redis_get error\r\n");
		freeReplyObject(reply);
		return -1;
	}
	if(reply->str == NULL) {
		printf("redis_get reply->str == NULL \r\n");
		freeReplyObject(reply);
		return -1;
	}
	strcpy(buff, reply->str);
	freeReplyObject(reply);

	printf("%s\r\n", buff);
	return 0;
}


int redis_put(char* buff)
{
	redisReply *reply = NULL;
	reply = redisCommand(redis_connect, "RPUSH %s %s", ack_key, buff);
	if (reply == NULL || reply->type == REDIS_REPLY_ERROR) {
		printf("redis_put error\r\n");
		freeReplyObject(reply);
		return -1;
	}
	freeReplyObject(reply);

	printf("%s\r\n", buff);
	return 0;
}

