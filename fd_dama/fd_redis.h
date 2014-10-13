
#ifndef _REDIS_INCLUDE__H__
#define _REDIS_INCLUDE__H__

int redis_init(void);
int redis_reinit(void);
int redis_clean(void);

int redis_get(char* buff);
int redis_put(char* buff);

int  redis_dbid;
char redis_ip[32];

#endif // #ifndef _REDIS_INCLUDE__H__

