/********************************** (C) COPYRIGHT *******************************
 * File Name          : main.c
 * Author             : WCH
 * Version            : V1.0.0
 * Date               : 2022/08/08
 * Description        : Main program body.
 *********************************************************************************
 * Copyright (c) 2021 Nanjing Qinheng Microelectronics Co., Ltd.
 * Attention: This software (modified or not) and binary are used for 
 * microcontroller manufactured by Nanjing Qinheng Microelectronics.
 *******************************************************************************/

/*
 *@Note
 *Multiprocessor communication mode routine:
 *Master:USART1_Tx(PD5)\USART1_Rx(PD6).
 *This routine demonstrates that USART1 receives the data sent by CH341 and inverts
 *it and sends it (baud rate 115200).
 *
 *Hardware connection:PD5 -- Rx
 *                     PD6 -- Tx
 *
 */

#include "debug.h"
#include <string.h>
#include <stdlib.h>
#include <ctype.h>


/* Global define */


/* Global Variable */
vu8 val;

/*********************************************************************
 * @fn      USARTx_CFG
 *
 * @brief   Initializes the USART2 & USART3 peripheral.
 *
 * @return  none
 */
void USARTx_CFG(void)
{
    GPIO_InitTypeDef  GPIO_InitStructure = {0};
    USART_InitTypeDef USART_InitStructure = {0};

    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOD | RCC_APB2Periph_USART1, ENABLE);

    /* USART1 TX-->D.5   RX-->D.6 */
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_5;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_Init(GPIOD, &GPIO_InitStructure);
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_6;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_Init(GPIOD, &GPIO_InitStructure);

    USART_InitStructure.USART_BaudRate = 115200;
    USART_InitStructure.USART_WordLength = USART_WordLength_8b;
    USART_InitStructure.USART_StopBits = USART_StopBits_1;
    USART_InitStructure.USART_Parity = USART_Parity_No;
    USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
    USART_InitStructure.USART_Mode = USART_Mode_Tx | USART_Mode_Rx;

    USART_Init(USART1, &USART_InitStructure);
    USART_Cmd(USART1, ENABLE);
}

/*
 * GPIO Settings
 */
void BUS_IN_SET();
void BUS_OUT_SET();
void ROM_OE(BitAction mode);
void Baker_data_OE(BitAction mode);
void ROM_WR(BitAction mode);
void Data_Latch(BitAction mode);
void Addr_LSB_Latch(BitAction mode);
void Addr_MSB_Latch(BitAction mode);

void GPIO_INIT()
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA|RCC_APB2Periph_GPIOC|RCC_APB2Periph_GPIOD, ENABLE);
    BUS_IN_SET();
    // PA
    GPIO_InitTypeDef GPIO_InitStructure = {0};
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_1|GPIO_Pin_2;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_2MHz;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    ROM_OE(Bit_SET);
    Addr_LSB_Latch(Bit_RESET);
    // PD
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0|GPIO_Pin_2|GPIO_Pin_3|GPIO_Pin_4|GPIO_Pin_7;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_2MHz;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_Init(GPIOD, &GPIO_InitStructure);
    Baker_data_OE(Bit_SET);
    ROM_WR(Bit_SET);
    Data_Latch(Bit_RESET);
    Addr_MSB_Latch(Bit_RESET);
}

void BUS_OUT_SET()
{
    GPIO_InitTypeDef GPIO_InitStructure = {0};
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_All;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_2MHz;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_Init(GPIOC, &GPIO_InitStructure);
}
void BUS_IN_SET()
{
    GPIO_InitTypeDef GPIO_InitStructure = {0};
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_All;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_2MHz;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_Init(GPIOC, &GPIO_InitStructure);
}

// Disable  -> BitSet
// Enable   -> BitReset
void ROM_OE(BitAction mode)
{
    GPIO_WriteBit(GPIOD, GPIO_Pin_4,mode);
}

// Disable  -> BitSet
// Enable   -> BitReset
void Baker_data_OE(BitAction mode)
{
    GPIO_WriteBit(GPIOA, GPIO_Pin_2,mode);
}

// Latch -> BitSet
// Hold  -> BitReset
void Data_Latch(BitAction mode)
{
    GPIO_WriteBit(GPIOD, GPIO_Pin_0,mode);
}

// Latch -> BitSet
// Hold  -> BitReset
void Addr_MSB_Latch(BitAction mode)
{
    GPIO_WriteBit(GPIOD, GPIO_Pin_7,mode);
}

// Latch -> BitSet
// Hold  -> BitReset
void Addr_LSB_Latch(BitAction mode)
{
    GPIO_WriteBit(GPIOA, GPIO_Pin_1,mode);
}

void ROM_WR(BitAction mode)
{
    GPIO_WriteBit(GPIOD, GPIO_Pin_3,mode);
}

/*
 * ROM Read/Write/Erc
 */
void Program_Byte(uint32_t addr ,uint16_t data);
uint16_t Read_Byte(uint32_t addr);
void Erase_All();
void Data_WR(uint32_t addr ,uint16_t data);
void Data_SET(uint16_t data);
void Addr_SET(uint32_t addr);
void Addr_LSB_SET(int addr_LSB);
void Addr_MSB_SET(int addr_MSB);


void Program_Byte(uint32_t addr ,uint16_t data)
{
    Data_WR(0x5555, 0xAA);
    Data_WR(0x2AAA, 0x55);
    Data_WR(0x5555, 0xA0);
    Data_WR(addr, data);
    Delay_Us(12);
}
uint16_t Read_Byte(uint32_t addr)
{
    Addr_SET(addr);
    BUS_IN_SET();
    Baker_data_OE(Bit_SET);//Data output disable
    ROM_WR(Bit_SET);
    ROM_OE(Bit_RESET);//ROM output enable
    uint16_t result = GPIO_ReadInputData(GPIOC);
    ROM_OE(Bit_SET);//ROM output disable
    return result;

}
void Erase_All()
{
    Data_WR(0x5555, 0xAA);
    Data_WR(0x2AAA, 0x55);
    Data_WR(0x5555, 0x80);
    Data_WR(0x5555, 0xAA);
    Data_WR(0x2AAA, 0x55);
    Data_WR(0x5555, 0x10);
    Delay_Ms(150);
}
void Data_WR(uint32_t addr ,uint16_t data)
{
    ROM_WR(Bit_SET);
    ROM_OE(Bit_SET);
    Data_SET(data);
    Addr_SET(addr);
    BUS_IN_SET();
    Baker_data_OE(Bit_RESET);
    ROM_WR(Bit_RESET);
    //Delay_Us(1);
    ROM_WR(Bit_SET);
    //Delay_Us(1);
    Baker_data_OE(Bit_SET);
    //Delay_Us(1);
}
void Data_SET(uint16_t data)
{
    ROM_OE(Bit_SET);//ROM output disable
    Baker_data_OE(Bit_SET);//Data output disable
    BUS_OUT_SET();// BUS output
    GPIO_Write(GPIOC,data);
    Addr_MSB_Latch(Bit_SET);
    Addr_LSB_Latch(Bit_SET);
    Data_Latch(Bit_SET);
    //Delay_Us(1);
    Data_Latch(Bit_RESET);
    BUS_IN_SET();
}

void Addr_SET(uint32_t addr)
{
    Addr_LSB_SET(addr&0xFF);
    Addr_MSB_SET((addr>>8) & 0xFF);
    //GPIO_WriteBit(GPIOD, GPIO_Pin_2, addr&0x10000 == 0 ? Bit_RESET : Bit_SET);
    GPIO_WriteBit(GPIOD, GPIO_Pin_2, Bit_RESET);
}
void Addr_LSB_SET(int addr_LSB)
{
    ROM_OE(Bit_SET);//ROM output disable
    Baker_data_OE(Bit_SET);//Data output disable
    BUS_OUT_SET();// BUS output
    GPIO_Write(GPIOC,addr_LSB);
    Addr_MSB_Latch(Bit_SET);
    Addr_LSB_Latch(Bit_SET);
    //Delay_Us(1);
    Addr_LSB_Latch(Bit_RESET);
    BUS_IN_SET();
}
void Addr_MSB_SET(int addr_MSB)
{
    ROM_OE(Bit_SET);//ROM output disable
    Baker_data_OE(Bit_SET);//Data output disable
    BUS_OUT_SET();// BUS output
    GPIO_Write(GPIOC,addr_MSB);
    Addr_MSB_Latch(Bit_SET);
    //Delay_Us(1);
    Addr_MSB_Latch(Bit_RESET);
    BUS_IN_SET();
}
/*
 * Command
 */

#define Buf_size 20
char serial_rx[Buf_size] = "";


int hex_str_to_int(char *str){
  char *endptr;
  long wk = strtol(str,&endptr,16);
  if (str == endptr) {
      return -1;
  }
  if (wk > 0xFFFFFF || wk < 0) {
      return -1;
  }
  return (int)wk;
}
void serial_buf_clear(){
    for(int i=0; i < Buf_size;i++){
        serial_rx[i] = '\0';
    }
}
void serialReceive(){
    char c;
    //文字列初期化
    serial_buf_clear();
    while(1){
        while(USART_GetFlagStatus(USART1, USART_FLAG_RXNE) == RESET)
        {/* waiting for receiving finish */}
        c = (USART_ReceiveData(USART1));

        size_t now = strlen(serial_rx);
        if(c == '\r'){
            continue;
        }
        if(c == '\n'){
            //10文字でなければクリア，10文字なら本処理に返す
            if(now>10) serial_buf_clear();
            else        return;
        }
        if(isprint(c)){
            if(now > 10){
                //10文字以上であれば受信データクリアして先頭から書き込み
                serial_buf_clear();
                serial_rx[0] = c;
            }else{
                serial_rx[now] = c;
            }
        }
    }
}
/*********************************************************************
 * @fn      main
 *
 * @brief   Main program.
 *
 * @return  none
 */
int main(void)
{
    NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);
    SystemCoreClockUpdate();
    Delay_Init();
    USART_Printf_Init(115200);
    USARTx_CFG();
    GPIO_INIT();
    Delay_Ms(1000);
    long now_address = 0;
    while(1)
    {
        serialReceive();
        char command = serial_rx[0];
        char Buf[14];
        char wk[10] = "";
        switch(command){
          case '@':
                  strncpy(wk,serial_rx+1,7);
                  now_address = hex_str_to_int(wk);
                  if(now_address == -1){
                      printf("E\n");
                      continue;
                  }
                  sprintf(Buf,"%06lX\n",now_address);
                  printf("%s",Buf);
                  break;
          case 'R':
                  printf("%02X\n",Read_Byte(now_address));
                  now_address++;
                  break;
          case 'W':
                  strncpy(wk,serial_rx+1,3);
                  long data = hex_str_to_int(wk);
                  if(data == -1 || data > 0xFF){
                      printf("E\n");
                      continue;
                  }
                  Program_Byte(now_address, (uint16_t)data);
                  printf("%02X\n",Read_Byte(now_address));
                  now_address++;
                  break;
          case 'D':
                  Erase_All();
                  printf("0\n");
                  break;
          case 'V':
                  Delay_Ms(10);
                  printf("FLASH Baker v1.0 (firm:v1.0)\n");
                  break;
          default:
                  printf("E\n");
        }
    }
}
