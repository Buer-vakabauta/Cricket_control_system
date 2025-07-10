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
char POS_X[4],POS_Y[4];
uint16_t pox,poy;
uint8_t flag=0;

// 定义宏
void main_loop(void);
void init();

//初始化
void init()
{
    Timer_Init_TIM1();
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
	Servo_setAngle(0,180,90,0);
    while (1){
        Button_updated();
        OLED_ShowNum(2,1,pox,3);
        OLED_ShowNum(2,8,poy,3);
        //OLED_ShowString(1,7,POS_X);
        //OLED_ShowString(3,7,POS_Y);
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
        //scanf("%s,%s",POS_X,POS_Y);
        if(data_ready){
            char *comma = strchr(uart_buffer, ',');
            if (comma) {
                *comma = '\0';  // 分割字符串
                pox = string_to_int(POS_X);
                poy = string_to_int(POS_Y);
            }
            data_ready = 0;
        }
        UART_clearBuffer();
    #if ENABLE_UART
    #endif
        TIM_ClearITPendingBit(TIM1, TIM_IT_Update);
    }
}