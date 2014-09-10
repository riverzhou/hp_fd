
#include <stdbool.h>
#include <stdio.h>
#include <windows.h>

#include "fd_ocr.h"

/******************************************************************************************************
CaptchaOCR.dll导出函数说明：

int VcodeInit(//失败返回-1
char[] //lib文件路径
);

-------以上函数用于初始化识别----------

bool GetVcode(  	//能识别返回真，否则返回假
int Index,		//值为1。
char* ImgBuffer, 	//验证码图像二进制数据
int ImgBufLen,		//验证码图像尺寸
char[] Vcode);		//返回的已识别验证码文本

-------以上函数用于识别验证码----------

******************************************************************************************************/

LPGetVcode GetVcode  = NULL ;

int ocr_init(void)
{
	HINSTANCE hInst = LoadLibraryA("CaptchaOCR.dll");	//载入CaptchaOCR.dll
	if (!hInst){
		printf("无法加载 CaptchaOCR.Dll !!");
		return -1;
	}

	LPInit VcodeInit = (LPInit)GetProcAddress(hInst, "VcodeInit");
	if ( VcodeInit == NULL) {
		printf("GetProcAddress VcodeInit 失败 !");
		return -1;
	}
	int index = VcodeInit ("key.lib");			//初始化 仅需调用此函数一次 切勿重复调用！
	if (index == -1){					//返回-1说明初始化失败
		printf("初始化失败 !");
		return -1;
	}

	GetVcode = (LPGetVcode)GetProcAddress(hInst, "GetVcode");
	if ( GetVcode == NULL) {
		printf("GetProcAddress GetVcode 失败 !");
		return -1;
	}

	return 0;
}


