
//
// Created by 17820 on 25-7-10.
//

#include "Button.h"
Button buttons[BUTTON_NUM]={
        {GPIO_Pin_10,1,1,0,0,0},
        {GPIO_Pin_11,1,1,0,0,0},
        {GPIO_Pin_12,1,1,0,0,0},
        //{GPIO_Pin_13,1,1,0,0,0},
        //{GPIO_Pin_14,1,1,0,0,0}
};

void Button_Init(){
    GPIO_InitTypeDef GPIO_InitStructure;
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB,ENABLE);

    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_10|GPIO_Pin_11|GPIO_Pin_12|GPIO_Pin_13|GPIO_Pin_14;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IPU;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOB,&GPIO_InitStructure);
}

void Button_updated(){
    uint32_t CurrentTime = TIM_GetCounter(TIM4);
    for(int i=0;i<BUTTON_NUM;i++){
        uint8_t pinState = GPIO_ReadInputDataBit(GPIOB,buttons[i].pin);
        if(pinState != buttons[i].LastState){
            buttons[i].debounceTime = CurrentTime;
        }
        if((CurrentTime - buttons[i].debounceTime) > DEBOUNCE_TIME){
            if(pinState != buttons[i].State){
                buttons[i].State = pinState;
                if(buttons[i].State == 0){buttons[i].pressed = 1;}
                else{buttons[i].released = 1;}
            }
        }
        buttons[i].LastState = pinState;
    }
}

uint8_t BUTTON1_IsReleased(void)
{
    if (buttons[0].released) {
        buttons[0].released = 0;
        return 1;
    }
    return 0;
}
uint8_t BUTTON2_IsReleased(void)
{
    if (buttons[1].released) {
        buttons[1].released = 0;
        return 1;
    }
    return 0;
}
uint8_t BUTTON3_IsReleased(void)
{
    if (buttons[2].released) {
        buttons[2].released = 0;
        return 1;
    }
    return 0;
}
uint8_t BUTTON4_IsReleased(void)
{
    if (buttons[3].released) {
        buttons[3].released = 0;
        return 1;
    }
    return 0;
}

uint8_t BUTTON5_IsReleased(void)
{
    if (buttons[4].released) {
        buttons[4].released = 0;
        return 1;
    }
    return 0;
}
