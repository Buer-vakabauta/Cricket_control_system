//模板工程
//
#include <settings.h>
#include <Delay.h>
#include <Timer.h>
#include "PWM.h"
//全局变量
uint8_t flag=0;
float angle1=135;
float angle2=135;

// 定义宏
void main_loop(void);
void init();

//初始化
void init()
{
    Timer_Init_TIM1();
    PWM_Init(1999, 71);
#if ENABLE_UART
    UART_Init(9600);
#endif
}
int main()
{
    init();
    Servo_setAngle(angle1,angle2);
	main_loop();
}


void main_loop(void)
{


    while (1){

#if ENABLE_UART
        esp_printf("%.2f,%.2f",angle1,angle2);
        if(strlen(uart_buffer)>0&&uart_buffer[0]=='#'){
            sscanf(uart_buffer,"#%f,%f",&angle1,&angle2);
            Servo_setAngle(135,135);
        }
        UART_clearBuffer();
		Delay_ms(200);
#endif
    }
}


//TIM1中断
void TIM1_UP_IRQHandler(void)
{
    if (TIM_GetITStatus(TIM1, TIM_IT_Update) == SET){
    #if ENABLE_UART
    #endif
        TIM_ClearITPendingBit(TIM1, TIM_IT_Update);
    }
}