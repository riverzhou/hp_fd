

CC = i686-w64-mingw32-gcc
STRIP = i686-w64-mingw32-strip

log_level = -D_LOG_LEVEL_=2
files = fd_dama.c


all:
	$(CC) 		$(log_level) -O2 -Wall -std=gnu99 ${files} -o fd_dama.exe
	$(STRIP)	fd_dama.exe


clean:
	@rm -rf *.o *.log *.dump *.pyc *.pyo *.ack *.req *.cookie __pycache__ core dump bad.jpg ./log/*
	@rm -rf *.exe


