//模板工程
//板球平衡
#include <settings.h>
#include <Delay.h>
#include <Timer.h>
#include "PWM.h"
#include <OLED.h>
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
	OLED_Init();
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


    while (1){

#if ENABLE_UART
		
        esp_printf("Hello");
		OLED_ShowString(1,1,"Start");
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