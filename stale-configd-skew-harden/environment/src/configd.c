#include "config.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#ifdef PROTOCOL_V2
#define ACTIVE 2
#else
#define ACTIVE PROTOCOL
#endif
#if ACTIVE == 3
static const char *tag="PROTO_V3";
#else
static const char *tag="PROTO_V2";
#endif
int main(int argc,char **argv){
  if(argc==3 && !strcmp(argv[1],"--hello")){int v=atoi(argv[2]+1);puts(v==ACTIVE?"HELLO_V3_OK":"ERR_VERSION");return v==ACTIVE?0:3;}
  if(argc==2 && !strcmp(argv[1],"--daemon")){FILE *f=fopen("var/lib/configd/live","w");if(!f)return 7;fprintf(f,"%s\n",tag);fclose(f);while(1)sleep(60);}
  puts(tag);return 0;
}
