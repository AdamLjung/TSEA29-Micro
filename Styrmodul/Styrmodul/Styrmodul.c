/*
 * Styrmodul.c
 *
 * Created: 2023-11-07
 *  Author: adalj586
 */ 


#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <stdio.h>

const int MAX_TURN = 1850;
const int MIN_TURN = 1150;
volatile uint8_t counter;

volatile int result;
volatile int tmpSpeed = 1500;
volatile int tmpAngle = 1500;
 

ISR(INT0_vect){
	//Starta A/D omvandling
	while(1){
		counter ++;
		counter --;
	}
	
	ADCSRA |= (1<<ADSC); // Start conversion
	
}

//JTAG on ATMEL-ICE ....55605

// Interrupt Service Routine till ADC - avbrottet :
ISR (ADC_vect ) {
	// kort rutin som tar hand om resultatet .
	
	PORTB = ADCH; // assigns the high value of ADCH to PORTB
	
}

// The initialization process normally consists of setting the baud rate, setting frame format and enabling the
// Transmitter or the Receiver depending on the usage

void USART_init(){
	UCSR0A = (1<<U2X0); // multiplier på oscillator frequency
	unsigned int baud = 8;//klockan är 8Mhz
	UBRR0L = (unsigned char)(baud);
	UCSR0B = (1<<RXEN0)|(1<<TXEN0)|(0<<UCSZ02);// Recieve enabled. Character size = 8-bit
	
	UCSR0C = (1<<UCSZ01)|(1<<UCSZ00)|(0<<USBS0)|(0<<UMSEL00)|(0<<UMSEL01); // Character size = 8-bit, 1 stoppbit
	
	
}


unsigned int USART_Receive( void) {
	
	TCNT3H = 0;
	TCNT3L = 0;
	int dt = 0;
	while(!(UCSR0A & (1<<RXC0) ) && dt < 15625){
		dt = (TCNT3H << 8 ) | (TCNT3L);
	}
	
	// Stop if no UART for two seconds (1 second = 7812.5, 8MHz / 1024)
	if(dt < 15625){
		return UDR0;
	}
	else{
		return -1;
	}
}


void USART_Transmit(unsigned char data){
	//UCSR0B = (1<<TXEN0);
	
	while(!(UCSR0A & (1<<UDRE0))) {}
	UDR0 = data;
	
	//UCSR0B = (0<<TXEN0);
}

int main(void)
{
	
	DDRD = 0xfe; // Port D 1111 1110
	
	//ADMUX = (1<<ADLAR); //Vänsterskiftat för höga delen till portb
	TCCR1A = (1<<WGM11)|(0<<WGM10)|(1<<COM1A1) |(0<<COM1A0)|(1<<COM1B1)|(0<<COM1B0);// Set OC0A on compare match,, Clear OC0A on Compare Match, set OC0A at BOTTOM, 
	TCCR1B = (1<<WGM13) | (1<<WGM12)| (0<<CS12)|(1<<CS11)|(0<<CS10);
	TCCR3B = (1<<CS32)|(0<<CS31)|(1<<CS30);



	// Klockan går 8 MHz vi delar på 8 i timer 1 för 1 MHz. 
	ICR1 = 20000; //period 1/1000 ms
	//Fartreglage. Teoretiskt max 2000
	OCR1A = 1500;
	//KOMMENTERA INTE UT UNDRE RAD
	// 1150-1850 SVÄNGRADIE (vänster-höger)
	OCR1B = 1500;
	//*********************************************************
	
	
	
	/* TIDIGARE PWM Frekvenser
	ICR1 = 199000;//199212										  
	OCR1A = 188; //Fartreglage
	OCR1B = 188; //Styrservo 146-230
	*/
	// PORTD = 0xff;// 0000 1000
// 	
// 	ADCSRA = (1<< ADEN)|(1<<ADIE); // ADEN = ADC enable, ADIE = ADC interrupt enable
// 	EICRA = (1<<ISC01)|(1<<ISC00);
// 	EIMSK = (1<<INT0); // External interrupt request 0

	
	//sei();// Enable interrupts
	//DDRD = 0x03; // Port 1 och 2 ut
	
	
	// variables:
	// OCR1A = pulse width, engine
	// 
	
	USART_init();
	
	//128
	//safe lower 134
	//safe upper 172
	//178
	
	//sätt lower bounds 
	
	
	// Denna är handshake för att hitta rätt port, AVR svarar med 0xfa på 0xfc och börjar sedan lyssna på styrsignaler. 
 	while(1){
 		result = USART_Receive();
 		if(result==-1){
			OCR1A = 1500;
			OCR1B = 1500;
			continue;
		}
		 
 		if(result == 0xfc){
 			
 			USART_Transmit(0xfa);
 			//UCSR0B = (0<<TXEN0);
 			break;
 		}else{
 			
 			USART_Transmit(0x01);
 		}
 	}


	while(1){
		/*
		while(!(UCSR0A & (1<<RXC0) )){
			
		}
		*/
		result = USART_Receive();
		
		// input * 20 + 1000
		//SPEED
		//if(result <= 0x7f) {
		// Failsafe för back, vi kan endast backa i en hastighet på 1400 (1.4ms) och värden under 4 stoppar den helt. 
		// Från UART får vi 0-50 där 25 är stilla och 50 är max, 0 är då full back utan de två första if som begränsar detta. 
		if (result <= 127) {
			tmpSpeed = result * 20 + 1000;
			if(result < 4){
				OCR1A = 1500;
			}
			else if(result < 25){
				OCR1A = 1400;
			}
			
			else if (tmpSpeed > 2000 || tmpSpeed < 1000) {
				OCR1A = 1500;
				
				OCR1B = 1500;
			} else {
				OCR1A = tmpSpeed;
			}
		//ANGLE
		// Hanterar styrservo, också clampat så att det inte kan gå över vissa värden, stoppar då bilen och sätter hjulen rakt. 
		} else {
			tmpAngle = (result & 127) * 15 + 1125;
			if(result == 0xfc){
				USART_Transmit(0xFA);
			}
			if (tmpAngle > 1875 || tmpAngle < 1125) {
				OCR1A = 1500;
				OCR1B = 1500;
			} else {
				OCR1B = tmpAngle;
			}
		}
		
	/*	
		//detta är för fart
		if(result == 0x0a){ 
			OCR1A = 1650;
		}else if(result ==0x0b){
			OCR1A = 1500;
		}
		
		//detta är för styr
		
		
		else if(result == 0x0c){
	
			OCR1B = 1500;
		}
		else if(result == 0x0d){
			OCR1B = 1800;
		}
		else if(result == 0x0e){
			OCR1B = 1300;
		}
		*/
	}
	
		//******************************************************************************** 
		//Kom ihåg if-sats för att begränsa styrservo. Intervallet ligger mellan 1150-1850!!
		//********************************************************************************  
		
		
		
		
		
    
}



