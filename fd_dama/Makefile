

CC = i686-w64-mingw32-gcc
STRIP = i686-w64-mingw32-strip

files = fd_base64.c  fd_dama.c  fd_ocr.c  fd_redis.c


all:
	$(CC) 				-O3 -march=core2 -msse2 -Wall -std=gnu99 ${files} -o fd_dama.exe   -L. -lhiredis_static -lws2_32 -mthreads
	$(CC) -D_DEBUG_			-O3 -march=core2 -msse2 -Wall -std=gnu99 ${files} -o fd_dama_d.exe -L. -lhiredis_static -lws2_32 -mthreads
	$(CC) -D_DEBUG_	-D_TEST_ 	-O3 -march=core2 -msse2 -Wall -std=gnu99 ${files} -o fd_dama_t.exe -L. -lhiredis_static -lws2_32 -mthreads
	$(STRIP)	fd_dama.exe  fd_dama_d.exe  fd_dama_t.exe


clean:
	@rm -rf *.o *.log *.dump *.pyc *.pyo *.ack *.req *.cookie __pycache__ core dump bad.jpg
	@rm -rf *.exe


