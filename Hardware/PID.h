#ifndef __PID_H
#define __PID_H

#define ZHONGZHI 0
#define position_zero 0
#include "stm32f10x.h"

typedef struct PID_structer {
    int16_t KP, KI, KD;
    int16_t error;
    int16_t last_error;
    int16_t error_sum;
} PID_structer;

void XTilt(int16_t tilt);
void YTilt(int16_t tilt);
void PID_init(PID_structer* PID_);
int16_t Pos_Circle(PID_structer* _PID ,int16_t Target_value,int16_t Current_value);
int16_t Speed_Circle(PID_structer* _PID ,int16_t Target_value,int16_t Current_value);
#endif
