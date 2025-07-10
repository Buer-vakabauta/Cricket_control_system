//
// Created by 17820 on 25-7-10.
//

#ifndef CLIONSTM32DEMO_BUTTON_H
#define CLIONSTM32DEMO_BUTTON_H
#include "stm32f10x.h"
//覆盖机械消抖时间通常10~50ms
#define DEBOUNCE_TIME 30
//按钮数量
#define BUTTON_NUM 5

typedef struct {
    uint16_t pin;
    uint8_t State;
    uint8_t LastState;
    uint32_t debounceTime;//消抖时间标志
    uint8_t pressed;
    uint8_t released;
}Button;

void Button_Init();
void Button_updated();
uint8_t BUTTON1_IsReleased(void);
uint8_t BUTTON2_IsReleased(void);
uint8_t BUTTON3_IsReleased(void);
uint8_t BUTTON4_IsReleased(void);
uint8_t BUTTON5_IsReleased(void);
#endif //CLIONSTM32DEMO_BUTTON_H
