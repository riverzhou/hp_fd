

CC = i686-w64-mingw32-gcc
STRIP = i686-w64-mingw32-strip

log_level = -D_LOG_LEVEL_=2
files = fd_base64.c  fd_dama.c  fd_ocr.c  fd_redis.c


all:
	$(CC) 		$(log_level) -O2 -Wall -std=gnu99 ${files} -o fd_dama.exe -L. -lhiredis_static -lws2_32 -mthreads 
	$(STRIP)	fd_dama.exe


clean:
	@rm -rf *.o *.log *.dump *.pyc *.pyo *.ack *.req *.cookie __pycache__ core dump bad.jpg
	@rm -rf *.exe


