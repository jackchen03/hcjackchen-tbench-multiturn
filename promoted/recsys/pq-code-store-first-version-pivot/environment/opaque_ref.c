#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint32_t u32(const unsigned char*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void p32(unsigned char*p,uint32_t v){p[0]=v;p[1]=v>>8;p[2]=v>>16;p[3]=v>>24;}
static uint32_t crc32b(const unsigned char*d,size_t n){uint32_t c=~0u;for(size_t i=0;i<n;i++){c^=d[i];for(int b=0;b<8;b++)c=(c>>1)^(0xedb88320u&(-(int32_t)(c&1)));}return~c;}
int main(int argc,char**argv){if(argc!=3)return 2;FILE*f=fopen(argv[1],"rb");if(!f)return 3;fseek(f,0,SEEK_END);long z=ftell(f);rewind(f);if(z<12)return 4;unsigned char*raw=malloc(z);if(!raw||fread(raw,1,z,f)!=(size_t)z)return 5;fclose(f);
 uint32_t n=u32(raw),m=u32(raw+4),bs=u32(raw+8);if(!n||!m||!bs||(size_t)z!=12u+(size_t)n*m)return 6;uint32_t nb=(n+bs-1)/bs,mb=(m+7)/8;size_t cap=24u+4u*nb+(size_t)n*(2u+mb+m);unsigned char*out=calloc(1,cap);memcpy(out,"PQD1",4);p32(out+4,n);p32(out+8,m);p32(out+12,bs);p32(out+16,nb);size_t pos=20+4u*nb;unsigned char*codes=raw+12;
 for(uint32_t b=0;b<nb;b++){p32(out+20+4*b,pos);uint32_t start=b*bs,count=start+bs>n?n-start:bs;memcpy(out+pos,codes+(size_t)start*m,m);pos+=m;for(uint32_t r=1;r<count;r++){unsigned char*prev=codes+(size_t)(start+r-1)*m,*cur=codes+(size_t)(start+r)*m;out[pos++]=1+mb+m;size_t mask=pos;pos+=mb;for(uint32_t j=0;j<m;j++)if(cur[j]!=prev[j]){out[mask+j/8]|=1u<<(j%8);out[pos++]=cur[j]^prev[j];}}}
 p32(out+pos,crc32b(out,pos));pos+=4;FILE*g=fopen(argv[2],"wb");if(!g||fwrite(out,1,pos,g)!=pos)return 7;fclose(g);free(raw);free(out);return 0;}
