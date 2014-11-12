
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <windows.h>

#include "fd_ocr.h"
#include "fd_base64.h"
#include "fd_redis.h"

#define MAX_BUFLEN	4096

/******************************************************************************************************
  bool GetVcode(  	//能识别返回真，否则返回假
  int Index,		//值为1。
  char* ImgBuffer, 	//验证码图像二进制数据
  int ImgBufLen,		//验证码图像尺寸
  char[] Vcode);		//返回的已识别验证码文本

//char result[7] = {0};						//定义一个字符串以接收验证码，这里验证码字符数是6，所以取7.
 ******************************************************************************************************/

/******************************************************************************************************
  int Base64Decode(char * buf, const char * base64code, int src_len );
 ******************************************************************************************************/

int init(void)
{
	if (redis_init() < 0)
		return -1;

	if (ocr_init()   < 0)
		return -1;

	return 0;
}

int get_image(char* buff, char* sid, char* type, char* timeout, char* image)
{
	int i = 0, n = 0;
	int p[3] = {0};

	int len = strlen(buff);

	for(n = 0; n < 3; n++) {
		for(i += 1; i < len; i++) {
			if (buff[i] == ',') {
				break;
			}
		}
		p[n] = i;
	}

	if (p[0] == len || p[1] == len || p[2] == len)
		return -1;

	if (p[0] == 0 || p[1] == 0 || p[2] == 0)
		return -1;

	memcpy(sid, buff, p[0]);

	memcpy(type, &(buff[p[0]+1]), p[1] - p[0] - 1);

	memcpy(timeout, &(buff[p[1]+1]), p[2] - p[1] - 1);

	memcpy(image, &(buff[p[2]+1]), len - p[2] - 1);

	return 0;
}

int make_result(char* buff, char* sid, char* code)
{
	strcat(buff, sid);
	strcat(buff, ",");
	strcat(buff, code);

	return 0;
}

int parse_config(int argc, char* argv[])
{
	if ( argc != 3 ){
		printf("usage:%s 192.168.1.90 5 \n",argv[0]);
		return -1;
	}

	int ip = 0;
	int db = 0;

	ip = inet_addr(argv[1]);
	if ( ip == INADDR_NONE ){
		printf("ip : %s invalid \n" , argv[1] );
		return -1;
	}

	db = atoi(argv[2]);
	if( db < 1 ){
		printf("db: %s  invalid \n" , argv[2] );
		return -1;
	}

	strcpy(redis_ip , argv[1]);
	redis_dbid = db;

	return 0;
}

int main(int argc, char* argv[])
{
	if( parse_config(argc, argv) < 0 ) {
		return -1;
	}

	if( init() < 0 ) {
		return -1;	
	}

	printf("init ok\r\n");

	char redis_inbuff[MAX_BUFLEN]   = {0};
	char redis_outbuff[MAX_BUFLEN]  = {0};
	char base64_inbuff[MAX_BUFLEN]  = {0};
	char base64_outbuff[MAX_BUFLEN] = {0};
	char dama_sid[MAX_BUFLEN]	= {0};
	char dama_type[MAX_BUFLEN]	= {0};
	char dama_timeout[MAX_BUFLEN]	= {0};
	char dama_code[MAX_BUFLEN]	= {0};

	while(true){
		memset(redis_inbuff,   0, sizeof(redis_inbuff));
		memset(redis_outbuff,  0, sizeof(redis_outbuff));
		memset(base64_inbuff,  0, sizeof(base64_inbuff));
		memset(base64_outbuff, 0, sizeof(base64_outbuff));
		memset(dama_sid,       0, sizeof(dama_sid));
		memset(dama_type,      0, sizeof(dama_type));
		memset(dama_timeout,   0, sizeof(dama_timeout));
		memset(dama_code,      0, sizeof(dama_code));

		int buff_len = 0;

		if (redis_get(redis_inbuff) < 0){
			if (redis_reinit() < 0)
				break;
			Sleep(1000);	// 1秒
			continue;
		}

		if (get_image(redis_inbuff, dama_sid, dama_type, dama_timeout, base64_inbuff) < 0)
			continue;
		if (dama_sid[0] == 0)
			continue;
		buff_len = Base64Decode(base64_outbuff, base64_inbuff, strlen(base64_inbuff));
		if (buff_len <= 0 || base64_outbuff[0] == 0){
			strcpy(dama_code, "000000");
		}
		else {
#ifndef _TEST_
			if (GetVcode(1, base64_outbuff, buff_len, dama_code) == false)
				strcpy(dama_code, "000000");
			else if (dama_code[5] == 0)
				strcpy(dama_code, "000000");
#else
			strcpy(dama_code, "000000");
#endif
		}
		make_result(redis_outbuff, dama_sid, dama_code);

		if (redis_put(redis_outbuff) < 0){
			if (redis_reinit() < 0)
				break;
			Sleep(1000);	// 1秒
			continue;
		}

		Sleep(1);		// 1毫秒
	}

	return 0;
}


