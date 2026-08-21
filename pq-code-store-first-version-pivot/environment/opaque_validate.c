#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint32_t u32(const unsigned char*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint32_t crc32b(const unsigned char*d,size_t n){uint32_t c=~0u;for(size_t i=0;i<n;i++){c^=d[i];for(int b=0;b<8;b++)c=(c>>1)^(0xedb88320u&(-(int32_t)(c&1)));}return~c;}
int main(int argc,char**argv){
 if(argc!=2)return 2;FILE*f=fopen(argv[1],"rb");if(!f)return 3;fseek(f,0,SEEK_END);long z=ftell(f);rewind(f);if(z<28)return 4;
 size_t size=(size_t)z;unsigned char*d=malloc(size);if(!d||fread(d,1,size,f)!=size)return 5;fclose(f);
 if(memcmp(d,"PQD1",4))return 6;uint32_t n=u32(d+4),m=u32(d+8),bs=u32(d+12),nb=u32(d+16);if(!n||!m||!bs||nb!=(n+bs-1)/bs)return 7;
 size_t head=20+4u*nb;if(head+4>size||crc32b(d,size-4)!=u32(d+size-4))return 8;uint32_t mb=(m+7)/8;size_t prior=0;
 for(uint32_t b=0;b<nb;b++){size_t p=u32(d+20+4*b),end=b+1<nb?u32(d+24+4*b):size-4;if(p<head||p>=end||end>size-4||(b&&p<=prior))return 9;prior=p;if(p+m>end)return 10;p+=m;uint32_t count=(b+1)*bs>n?n-b*bs:bs;
  for(uint32_t r=1;r<count;r++){if(p+1+mb>end||d[p]!=(unsigned char)(1+mb+m))return 11;p++;uint32_t changed=0;for(uint32_t j=0;j<m;j++)changed+=(d[p+j/8]>>(j%8))&1;p+=mb+changed;if(p>end)return 12;}if(p!=end)return 13;}
 free(d);return 0;}
