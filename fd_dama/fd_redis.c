
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#include "hiredis.h"

#include "fd_redis.h"

#define MAX_BUFLEN	4096

char redis_pass[]  	= "river";
int  redis_dbid  	= 0;
char redis_ip[32] 	= {0};
int  redis_port 	= 6379;

char req_key[] 	 = "req_image";
char ack_key[] 	 = "ack_number";

//=====================================================================================

redisContext *redis_connect;

int redis_init(void)
{
	redis_connect = NULL;
	redis_connect = redisConnect((char*)redis_ip, redis_port);
	if (redis_connect == NULL) {
		printf("Connection error: (NULL)\n");
		return -1;
	}
	if (redis_connect->err) {
		printf("Connection error: %s\n", redis_connect->errstr);
		redisFree(redis_connect);
		redis_connect = NULL;
		return -1;
	}

	redisReply *reply = NULL;
	reply = redisCommand(redis_connect, "AUTH %s", redis_pass);
	if (reply == NULL ) {
		printf("AUTH error: (NULL) %s\n", redis_pass);
		redisFree(redis_connect);
		redis_connect = NULL;
		return -1;
	}
	if (reply->type == REDIS_REPLY_ERROR) {
		printf("AUTH error: %s\n", redis_pass);
		freeReplyObject(reply);
		redisFree(redis_connect);
		redis_connect = NULL;
		return -1;
	}
	freeReplyObject(reply);

	reply = redisCommand(redis_connect, "SELECT %d", redis_dbid);
	if (reply == NULL ) {
		printf("SELECT error: (NULL) %d\n", redis_dbid);
		redisFree(redis_connect);
		redis_connect = NULL;
		return -1;
	}
	if (reply->type == REDIS_REPLY_ERROR) {
		printf("SELECT error: %d\n", redis_dbid);
		freeReplyObject(reply);
		redisFree(redis_connect);
		redis_connect = NULL;
		return -1;
	}
	freeReplyObject(reply);

	return 0;
}

int redis_clean(void)
{
	if (redis_connect != NULL){
		redisFree(redis_connect);
		redis_connect = NULL;
	}
	return 0;
}

int redis_reinit(void)
{
	redis_clean();
	int ret = -1;
	while(true){
		ret = redis_init();
		if ( ret == 0 ) {
			break;
		}
		Sleep(1000);	// 1秒
	}
	return 0;
}

int redis_get(char* buff)
{
	redisReply *reply = NULL;
	reply = redisCommand(redis_connect, "BLPOP %s 0", req_key);
	if (reply == NULL ) {
		buff[0] = 0;
		printf("redis_get error(NULL)\r\n");
		return -1;
	}
	if (reply->type == REDIS_REPLY_ERROR) {
		buff[0] = 0;
		printf("redis_get error\r\n");
		freeReplyObject(reply);
		return -1;
	}
	if(reply->element[1]->str == NULL) {
		buff[0] = 0;
		printf("redis_get reply->element[1]->str == NULL \r\n");
		freeReplyObject(reply);
		return -1;
	}
	strncpy(buff, reply->element[1]->str, MAX_BUFLEN);
	freeReplyObject(reply);

#ifdef _DEBUG_
	printf("%s\r\n", buff);
#endif
	return 0;
}

int redis_put(char* buff)
{
	redisReply *reply = NULL;
	reply = redisCommand(redis_connect, "RPUSH %s %s", ack_key, buff);
	if (reply == NULL ) {
		printf("redis_put error(NULL)\r\n");
		return -1;
	}
	if (reply->type == REDIS_REPLY_ERROR) {
		printf("redis_put error\r\n");
		freeReplyObject(reply);
		return -1;
	}
	freeReplyObject(reply);

#ifdef _DEBUG_
	printf("%s\r\n", buff);
#endif
	return 0;
}

