//
// Created by Buer_vakabauta on 2024/10/30.
//

#ifndef CLIONSTM32DEMO_UARTS_H
#define CLIONSTM32DEMO_UARTS_H
#include "stm32f10x.h"
extern char uart_buffer[];
extern int16_t ball_posx,ball_posy;
extern int16_t Xpid,Ypid;

void UART_Init(uint32_t baud_rate);
float string_to_float(const char *str);
int string_to_int(const char *str);
void UART_SendChar(char c);
void UART_SendString(const char* str);
char UART_ReceiveChar(void);
void UART_Send_num(int16_t num,uint8_t length);
void UART_clearBuffer(void);
void USART_ReceiveString(void);
#endif //CLIONSTM32DEMO_UARTS_H
