#include <wiringPi.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "PCD8544.h"

// pin setup
int _din = 1;
int _sclk = 0;
int _dc = 2;
int _rst = 4;
int _cs = 3;

#define HEIGHT 8
  
// lcd contrast 
//may be need modify to fit your screen!  normal: 30- 90 ,default is:45 !!!maybe modify this value!
int contrast = 60;  
  
int main(int argc, char *argv[]) 
{
  if (wiringPiSetup() == -1)
  {
	printf("wiringPi-Error\n");
    exit(1);
  }
  // init and clear lcd
  LCDInit(_sclk, _din, _dc, _cs, _rst, contrast);
  LCDclear();
  
  // clear lcd
  LCDclear();
  // build screen
  for (int line=0; line < argc-1; line+=1) {
    LCDdrawstring(0, line*HEIGHT, argv[line+1]);
  }
  LCDdisplay();
  return 0;
}
