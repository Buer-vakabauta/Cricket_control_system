#include "PID.h"
#include "stm32f10x.h"
#include "Motor.h"
#include "stdio.h"
#include "UART.h"
#include <PWM.h>
#include "Delay.h"

//使用四个舵机
#define MAX_ANGLE_X 260
#define MID_ANGLE_X 180
#define MIN_ANGLE_X 90
#define MAX_ANGLE_Y 260
#define MID_ANGLE_Y 180
#define MIN_ANGLE_Y 90

uint16_t X_H_Angle,X_L_Angle,Y_H_Angle,Y_L_Angle;
PID_structer XSite;
PID_structer YSite;
PID_structer XSpeed;
PID_structer YSpeed;

void PID_init(PID_structer* PID_){
    PID_->error=0;
    PID_->last_error=0;
    PID_->error_sum=0;
}

//两个舵机控制一边的高低,pid输出需要的tilt的值，从而同时控制两个舵机
void XTilt(int16_t tilt){
    X_H_Angle = MID_ANGLE_X + tilt;
    X_L_Angle = MID_ANGLE_X - tilt;
    Servo_setAngle(X_H_Angle,X_L_Angle,-1,-1);
}
void YTilt(int16_t tilt){
    Y_H_Angle= MID_ANGLE_Y + tilt;
    Y_L_Angle= MID_ANGLE_Y - tilt;
    Servo_setAngle(-1,-1,Y_H_Angle,Y_L_Angle);
}

//速度-位置串级pid，
//位置环为内环，输入预期位置和当前位置,输出预期速度
//速度环为外环，输入预期速度（位置环的输出值）和当前速度，输出舵机的角度值
int16_t Pos_Circle(PID_structer* _PID ,int16_t Target_value,int16_t Current_value){
    _PID->last_error=_PID->error;
    _PID->error=Target_value-Current_value;
    _PID->error_sum+=_PID->error;
    if(_PID->error_sum>100) _PID->error_sum=100;
    else if(_PID->error_sum<-100) _PID->error_sum=-100;
    int16_t result=0;
    result=_PID->KP*_PID->error + (_PID->KI*_PID->error_sum)/10 - _PID->KD*(_PID->error-_PID->last_error);
    //char buffer[16];
    //sprintf(buffer,"PWM:%d\n",result);
    //UART_SendString(buffer);
    if(result>=1999) return 1999;
    else if(result<=-1999) return -1999;
    return result;
}

int16_t Speed_Circle(PID_structer* _PID ,int16_t Target_value,int16_t Current_value){
    _PID->last_error=_PID->error;
    _PID->error=Target_value-Current_value;
    _PID->error_sum+=_PID->error;
    if(_PID->error_sum>100) _PID->error_sum=100;
    else if(_PID->error_sum<-100) _PID->error_sum=-100;
    int16_t result=0;
    result=_PID->KP*_PID->error+(_PID->KI*_PID->error_sum)/10-_PID->KD*(_PID->error-_PID->last_error);
    //char buffer[16];
    //sprintf(buffer,"PWM:%d\n",result);
    //UART_SendString(buffer);
    if(result>=270) return 270;
    else if(result<=90) return 90;
    return result;
}
