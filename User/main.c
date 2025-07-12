//模板工程
//板球平衡系统
#include <settings.h>
#include <Delay.h>
#include <Timer.h>
#include "PWM.h"
#include <OLED.h>
#include <UART.h>
#include <Button.h>
//全局变量
uint8_t flag=0;
uint8_t i=6;
uint8_t j=1;
uint8_t t=1;
uint16_t Current_angle = 0;
// 定义宏
void main_loop(void);
void init();
void Button_detect();
//初始化
void init()
{
    Timer_Init_TIM4();
    PWM_Init(19999, 71);
	OLED_Init();
    Button_Init();

#if ENABLE_UART
    UART_Init(9600);
#endif
}

int main()
{
    init();
	main_loop();
}

void main_loop(void)
{
    OLED_ShowString(1,1,"Task:");
    OLED_ShowString(3,1,"Y OR N:");
    //Servo_setAngle(270,270,270,270);
	//Servo_setAngle(180,180,180,180);
	//Servo_setAngle(180,180,180,90);
	//Servo_setAngle(180,180,90,90);
	//Servo_setAngle(180,0,180,180);
	//Servo_setAngle(180,180,180,0);
    //Servo_setAngle(97,180,180,180);
	
    while (1){
        Button_updated();
        Button_detect();
        OLED_ShowSignedNum(2,1,ball_posx,3);
        OLED_ShowSignedNum(2,8,ball_posy,3);
        //OLED_ShowString(4,1,uart_buffer);
        OLED_ShowNum(4,1,Current_angle,3);
      #if ENABLE_UART
        //UART_SendString("task2");
		//OLED_ShowString(1,1,"Start");
        //UART_clearBuffer();
		//Delay_ms(200);
#endif
    }
}

void Button_detect(){
    if(BUTTON2_IsReleased()==1){
        //i = (i == 1) ? 6 : (i - 1);
        i = (i % 6) + 1;
        UART_Send_num(i,2);
        OLED_ShowString(1,6,"task");
        OLED_ShowNum(1,11,i,1);
        OLED_ShowString(3,9,"N");
    };
    if(BUTTON3_IsReleased()==1)
    {
        UART_SendString("Y");
        switch (i) {
            case 1:
                j += 1;
                Current_angle = 180+j;
                Servo_setAngle(Current_angle,Current_angle,Current_angle,Current_angle);
                break;
            case 2:
                t += 1;
                Current_angle = 180 - t;
                Servo_setAngle(Current_angle,Current_angle,Current_angle,Current_angle);
                break;
            case 3:
                t += 1;
                Current_angle = 90 + t;
                Servo_setAngle(Current_angle,Current_angle,Current_angle,Current_angle);
                break;
            case 4:
                
                t += 1;
                Current_angle = 90 - t;
                Servo_setAngle(Current_angle,Current_angle,Current_angle,Current_angle);
                break;
            case 5:
                Servo_setAngle(90,0,0,0);
                break;
            case 6:
                Servo_setAngle(0,0,0,0);
                break;
            default:
                Servo_setAngle(180,180,180,180);
                break;
        }
        OLED_ShowString(3,9,"Y");
    }
}