
#include <stdio.h>
#include <string.h>

#include "hiredis.h"

#include "fd_redis.h"

#define MAX_BUFLEN	4096

//char server_ip[] = "172.18.1.26";
//int  server_port = 6379;
//char password[]  = "river";
//int  redis_dbid  = 9;

char server_ip[] = "192.168.1.90";
int  server_port = 6379;
char password[]  = "river";
int  redis_dbid  = 5;

char req_key[] 	 = "req_image";
char ack_key[] 	 = "ack_number";

//=====================================================================================

redisContext *redis_connect;

int redis_init(void)
{
	redis_connect = redisConnect((char*)server_ip, server_port);
	if (redis_connect->err) {
		printf("Connection error: %s\n", redis_connect->errstr);
		redisFree(redis_connect);
		return -1;
	}

	redisReply *reply = NULL;
	reply= redisCommand(redis_connect, "AUTH %s", password);
	if (reply->type == REDIS_REPLY_ERROR) {
		printf("AUTH error: %s\n", password);
		freeReplyObject(reply);
		redisFree(redis_connect);
		return -1;
	}
	freeReplyObject(reply);

	reply = redisCommand(redis_connect, "SELECT %d", redis_dbid);
	if (reply->type == REDIS_REPLY_ERROR) {
		printf("SELECT error: %d\n", redis_dbid);
		freeReplyObject(reply);
		redisFree(redis_connect);
		return -1;
	}
	freeReplyObject(reply);

	return 0;
}

int redis_clean(void)
{
	if (redis_connect != NULL)
		redisFree(redis_connect);
	return 0;
}

int redis_reinit(void)
{
	redis_clean();
	return redis_init();
}

int redis_get(char* buff)
{
	redisReply *reply = NULL;
	reply = redisCommand(redis_connect, "BLPOP %s 0", req_key);
	if (reply == NULL || reply->type == REDIS_REPLY_ERROR) {
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
	if (reply == NULL || reply->type == REDIS_REPLY_ERROR) {
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

