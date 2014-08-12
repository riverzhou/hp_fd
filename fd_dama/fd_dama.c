
#include <stdbool.h>
#include <stdio.h>
#include <windows.h>

/******************************************************************************************************
CaptchaOCR.dll导出函数说明：

int VcodeInit(		//失败返回-1
char[] Password);
paasword ="XSE"

-------以上函数用于初始化识别----------

bool GetVcode(  	//能识别返回真，否则返回假
int Index,		//值为1。
char* ImgBuffer, 	//验证码图像二进制数据
int ImgBufLen,		//验证码图像尺寸
char[] Vcode);		//返回的已识别验证码文本

-------以上函数用于识别验证码----------

******************************************************************************************************/

//char result[7] = {0};						//定义一个字符串以接收验证码，这里验证码字符数是6，所以取7.

typedef int  (CALLBACK* LPInit)(char[]);
typedef bool (CALLBACK* LPGetVcode)(int,char*,int,char[]);
LPGetVcode GetVcode = NULL;					//识别函数

int init(void)
{
	HINSTANCE hInst = LoadLibraryA("CaptchaOCR.dll");	//载入CaptchaOCR.dll
	if (!hInst){
		printf("无法加载 CaptchaOCR.Dll !!");
		return -1;
	}

	LPInit VcodeInit = (LPInit)GetProcAddress(hInst, "VcodeInit");
	int index = VcodeInit ("XSE");				//初始化 仅需调用此函数一次 切勿重复调用！
	if (index == -1){					//返回-1说明初始化失败
		printf("初始化失败 !");
		return -1;
	}

	GetVcode = (LPGetVcode)GetProcAddress(hInst, "GetVcode");

	return 0;
}

int main(void)
{
	if( init() < 0 ) {
		return -1;	
	}

	printf("dll load ok");
	return 0;
}


