
#include "mbed.h"
 
// Hardware Quadrature Encoder ABZ for Nucleo F401RE
// Output on debug port to host PC @ 9600 baud
// 
// By Nigel Webb, November 2014
  
/* Connections TIM2
   PA_15 = Encoder A
   PB_9 = Encoder B
   PA_5 = Encoder Z 
*/ 
/* Connections TIM5 -NOT WORKING IN MBED
   PA_0 = Encoder A
   PA_1 = Encoder B
   PA_4 = Encoder Z 
*/
 
//InterruptIn ZPulse_TIM2(PA_5) ; // Setup Interrupt for Z Pulse (TIM2)
  
//InterruptIn ZPulse_TIM4(PA_5) ; // Setup Interrupt for Z Pulse (TIM2)
 
void EncoderInitialiseTIM2(void) {
    
     //TIM2
    // configure GPIO PA15 & PB9 as inputs for Encoder 
            RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;  // Enable clock for GPIOA
            GPIOA->MODER   |= GPIO_MODER_MODER15_1;    // PA15 as Alternate Function
            GPIOA->OTYPER  |= GPIO_OTYPER_OT_15;        // PA05 as Inputs
            GPIOA->OSPEEDR |= GPIO_OSPEEDER_OSPEEDR15;      // Low speed
            GPIOA->PUPDR   |= GPIO_PUPDR_PUPDR15_1  ;// Pull Down
            GPIOA->AFR[0]  |= 0x00000000 ;        // AF01 for PA15
            GPIOA->AFR[1]  |= 0x10000000 ;        // AF01 for PA15
 
            RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;        // Enable clock for GPIOB
            GPIOB->MODER    |= GPIO_MODER_MODER9_1 ; //PB09  as Alternate Function   /*!< GPIO port mode register,
            GPIOB->OTYPER   |= GPIO_OTYPER_OT_9 ;    // PB09 as Inputs               /*!< GPIO port output type register,
            GPIOB->OSPEEDR |= GPIO_OSPEEDER_OSPEEDR9;// Low speed                        /*!< GPIO port output speed register
            GPIOB->PUPDR   |= GPIO_PUPDR_PUPDR9_1  ;// Pull Down
            GPIOB->AFR[0]  |= 0x00000000 ;        // AF01 for PB9
            GPIOB->AFR[1]  |= 0x00000010;         // AF01 for PB9
                                                    //                                  /*!< GPIO alternate function registers,     Address offset: 0x20-0x24 */
   
    // configure TIM2 as Encoder input
    RCC->APB1ENR |= 0x00000001;  // Enable clock for TIM2
 
    TIM2->CR1   = 0x0001;     // CEN(Counter ENable)='1'     < TIM control register 1
    TIM2->SMCR  = 0x0003;     // SMS='011' (Encoder mode 3)  < TIM slave mode control register
    TIM2->CCMR1 = 0xF1F1;     // CC1S='01' CC2S='01'         < TIM capture/compare mode register 1
    TIM2->CCMR2 = 0x0000;     //                             < TIM capture/compare mode register 2
    TIM2->CCER  = 0x0011;     // CC1P CC2P                   < TIM capture/compare enable register
    TIM2->PSC   = 0x0000;     // Prescaler = (0+1)           < TIM prescaler
    TIM2->ARR   = 0xffffffff; // reload at 0xfffffff         < TIM auto-reload register
  
    TIM2->CNT = 0x0000;  //reset the counter before we use it  
   
}


void EncoderInitialiseTIM4(void) {
    
     //TIM4
    // configure GPIO PA15 & PB9 as inputs for Encoder 
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;  // Enable clock for GPIOA
    //stm32f4xx.h
    GPIOB->MODER |= GPIO_MODER_MODER6_1 | GPIO_MODER_MODER7_1;         //PB6 & PB7 as Alternate Function   /*!< GPIO port mode register,               Address offset: 0x00      */
    GPIOB->OTYPER |= GPIO_OTYPER_OT_6 | GPIO_OTYPER_OT_7;              //PB6 & PB7 as Inputs               /*!< GPIO port output type register,        Address offset: 0x04      */
    GPIOB->OSPEEDR |= GPIO_OSPEEDER_OSPEEDR6 | GPIO_OSPEEDER_OSPEEDR7; //Low speed                         /*!< GPIO port output speed register,       Address offset: 0x08      */
    GPIOB->PUPDR |= GPIO_PUPDR_PUPDR6_1 | GPIO_PUPDR_PUPDR7_1;         //Pull Down                         /*!< GPIO port pull-up/pull-down register,  Address offset: 0x0C      */
    GPIOB->AFR[0] |= 0x22000000;                                       //AF02 for PB6 & PB7                /*!< GPIO alternate function registers,     Address offset: 0x20-0x24 */
    GPIOB->AFR[1] |= 0x00000000;                                       //nibbles here refer to gpio8..15   /*!< GPIO alternate function registers,     Address offset: 0x20-0x24 */
    /*!< GPIO alternate function registers,     Address offset: 0x20-0x24 */
    RCC->APB1ENR |= RCC_APB1ENR_TIM4EN;

    TIM4->CR1 = 0x0001;                // CEN(Counter ENable)='1'     < TIM control register 1
    TIM4->SMCR = TIM_ENCODERMODE_TI12; //               < TIM slave mode control register
    //TIM_ENCODERMODE_TI1 input 1 edges trigger count
     //TIM_ENCODERMODE_TI2 input 2 edges trigger count
    //TIM_ENCODERMODE_TI12 all edges trigger count
    TIM4->CCMR1 = 0xF1F1; // CC1S='01' CC2S='01'         < TIM capture/compare mode register 1
    //0xF nibble sets up filter
    TIM4->CCMR2 = 0x0000;                       //                             < TIM capture/compare mode register 2
    TIM4->CCER = TIM_CCER_CC1E | TIM_CCER_CC2E; //     < TIM capture/compare enable register
    TIM4->PSC = 0x0000;                         // Prescaler = (0+1)           < TIM prescaler
    TIM4->ARR = 0xffff;                         // reload at 0xfffffff         < TIM auto-reload register

    TIM4->CNT = 0x0000; //reset the counter before we use it
 
 /*
    // configure TIM2 as Encoder input
    RCC->APB1ENR |= 0x00000001;  // Enable clock for TIM2
 
    TIM2->CR1   = 0x0001;     // CEN(Counter ENable)='1'     < TIM control register 1
    TIM2->SMCR  = 0x0003;     // SMS='011' (Encoder mode 3)  < TIM slave mode control register
    TIM2->CCMR1 = 0xF1F1;     // CC1S='01' CC2S='01'         < TIM capture/compare mode register 1
    TIM2->CCMR2 = 0x0000;     //                             < TIM capture/compare mode register 2
    TIM2->CCER  = 0x0011;     // CC1P CC2P                   < TIM capture/compare enable register
    TIM2->PSC   = 0x0000;     // Prescaler = (0+1)           < TIM prescaler
    TIM2->ARR   = 0xffffffff; // reload at 0xfffffff         < TIM auto-reload register
  
    TIM2->CNT = 0x0000;  //reset the counter before we use it  
*/
}


// Z Pulse routine
void ZeroEncoderCount() {
    TIM4->CNT=0 ; //reset count to zero
}
 
int main() {
    // EncoderInitialise() ;
    EncoderInitialiseTIM4();
   
    //ZPulse_TIM2.rise(&ZeroEncoderCount) ; //Setup Interrupt for rising edge of Z pulse TIM2
    //ZPulse_TIM2.mode(PullDown) ; // Set input as pull down
     
    unsigned int EncoderPositionTIM2 ;
    unsigned int EncoderPositionTIM4 ;

    while (true) {
        // Print Encoder Quadrature count to debug port every 0.5 seconds
       // EncoderPositionTIM2 = TIM2->CNT ; // Get current position from Encoder
        EncoderPositionTIM4 = TIM4->CNT ;

                printf("Encoder Position TIM4 %i\r\n  ", EncoderPositionTIM4);
                     
        
        wait(0.5);
    }
       
}