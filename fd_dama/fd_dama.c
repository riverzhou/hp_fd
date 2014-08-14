
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
	if (ocr_init()   < 0)
		return -1;

	if (redis_init() < 0)
		return -1;

	return 0;
}

int get_image(char* buff, char* sid, char* image)
{
	int i   = 0;
	int len = strlen(buff);

	for(i = 0; i < len; i++) {
		if (buff[i] == ',') {
			break;
		}
	}

	if (i == len)
		return -1;

	memcpy(sid, buff, i);
	memcpy(image, &(buff[i+1]), len - i - 1);

	return 0;
}

int make_result(char* buff, char* sid, char* code)
{
	strcat(buff, sid);
	strcat(buff, ",");
	strcat(buff, code);

	return 0;
}

int main(void)
{
	if( init() < 0 ) {
		return -1;	
	}

	printf("init ok\r\n");

	char redis_inbuff[MAX_BUFLEN]   = {0};
	char redis_outbuff[MAX_BUFLEN]  = {0};
	char base64_inbuff[MAX_BUFLEN]  = {0};
	char base64_outbuff[MAX_BUFLEN] = {0};
	char dama_sid[MAX_BUFLEN]	= {0};
	char dama_code[MAX_BUFLEN]	= {0};

	while(true){
		memset(redis_inbuff,   0, sizeof(redis_inbuff));
		memset(redis_outbuff,  0, sizeof(redis_outbuff));
		memset(base64_inbuff,  0, sizeof(base64_inbuff));
		memset(base64_outbuff, 0, sizeof(base64_outbuff));
		memset(dama_sid,       0, sizeof(dama_sid));
		memset(dama_code,      0, sizeof(dama_code));

		int buff_len = 0;

		if (redis_get(redis_inbuff) < 0)
			continue;
		if (get_image(redis_inbuff, dama_sid, base64_inbuff) < 0)
			continue;
		if (dama_sid[0] == 0)
			continue;
		buff_len = Base64Decode(base64_outbuff, base64_inbuff, strlen(base64_inbuff));
		if (buff_len <= 0 || base64_outbuff[0] == 0){
			strcpy(dama_code, "000000");
		}
		else {
			if (GetVcode(1, base64_outbuff, buff_len, dama_code) == false)
				strcpy(dama_code, "000000");
			else if (dama_code[5] == 0)
				strcpy(dama_code, "000000");
		}
		make_result(redis_outbuff, dama_sid, dama_code);
		redis_put(redis_outbuff);
	}

	return 0;
}


