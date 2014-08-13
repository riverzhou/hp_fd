
#ifndef _REDIS_INCLUDE__H__
#define _REDIS_INCLUDE__H__

int redis_init(void);

int redis_get(char* buff);
int redis_put(char* buff);

#endif // #ifndef _REDIS_INCLUDE__H__

