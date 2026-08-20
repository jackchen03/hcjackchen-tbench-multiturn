#include <ctype.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct{unsigned char*d;size_t n,c;}Buf; static void put(Buf*b,unsigned char x){if(b->n==b->c){b->c=b->c?b->c*2:256;b->d=realloc(b->d,b->c);}b->d[b->n++]=x;}
static int b64(char c){if(c>='A'&&c<='Z')return c-'A';if(c>='a'&&c<='z')return c-'a'+26;if(c>='0'&&c<='9')return c-'0'+52;if(c=='+')return 62;if(c=='/')return 63;return -1;}
static Buf decode(const char*s,size_t n){Buf o={0};int val=0,bits=-8;for(size_t i=0;i<n;i++){if(s[i]=='=')break;int x=b64(s[i]);if(x<0)continue;val=(val<<6)|x;bits+=6;if(bits>=0){put(&o,(val>>bits)&255);bits-=8;}}return o;}
static void footer(const unsigned char*p,size_t n){unsigned a=0x11,b=0x1f;for(size_t i=0;i<n;i++){a=(a+p[i])&255;b=(b+a)&255;}fputc(a,stdout);fputc(b,stdout);}
int main(void){Buf in={0},e={0};int ch;while((ch=fgetc(stdin))!=EOF)put(&in,(unsigned char)ch);char*start=strchr((char*)in.d,'[');if(!start)return 2;char*p=start+1;while(*p&&*p!=']'){while(*p&&*p!='"'&&*p!=']')p++;if(*p==']')break;char*q=++p;while(*q&&*q!='"')q++;Buf raw=decode(p,q-p);put(&e,0xaa);put(&e,0x55);for(size_t i=0;i<raw.n;i++){put(&e,raw.d[i]);if(raw.d[i]==0xaa&&i+1<raw.n&&(raw.d[i+1]==0x55||raw.d[i+1]==0x00))put(&e,0x00);}free(raw.d);p=q+1;}size_t off=0;while(e.n-off>=16){fwrite(e.d+off,1,16,stdout);footer(e.d+off,16);off+=16;}size_t rem=e.n-off;fwrite(e.d+off,1,rem,stdout);footer(e.d+off,rem);size_t v=rem;do{unsigned char byte=v&0x7f;v>>=7;if(v)byte|=0x80;fputc(byte,stdout);}while(v);free(in.d);free(e.d);return 0;}
