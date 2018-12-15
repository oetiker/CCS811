CFLAGS=-c -Wall -O2

all: ccs811demo

libccs811.a: ccs811.o
	$(AR) rcs $@ $^

%.o : %.c
	$(CC) -I. -c $(CFLAGS) $< -o $@
        
ccs811demo: ccs811demo.o libccs811.a
	$(CC) $(CFLAGS) $^ -o $@ -L. -lccs811

clean:
	-rm *.o libccs811.a ccs811demo
