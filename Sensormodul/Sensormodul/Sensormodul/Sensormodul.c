/*
 * Sensormodul.c
 *
 * Created: 2023-11-10 10:25:25
 *  Author: adalj586
 */

// Petters skvallersignaler:
// PA0=timer, PA1=INT0, PA2=main.cli, PA3=main.counter, PA4.toggle=INT0


//4565
//#define F_CPU 8000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
//#include <util/delay.h>

volatile uint8_t timer0 = 0;
volatile uint8_t counter = 0;


volatile uint8_t timer = 0;


volatile long sensorCount = 0;



ISR (INT0_vect){
	sensorCount++;
}

//Timer0 plussas varje 32 ms, då TCNT0 overflowas. TCNT0 är ett 8-bits register.
//Så för att komma så nära en sekund som möjligt så räknar vi upp till 31. Det blir 31*0.032 = 0.992
//Counter räknar då sekunder
//Just nu i den är koden under skickas det per 1/10 sek. För 1 sek sätt timer0 == 31.
ISR (TIMER0_OVF_vect){

	timer0++;
	if (timer0 == 3) {
		timer0 = 0;
		counter++;
	}
}

void isr_init(){
    //External
	EICRA = (1<<ISC01)|(1<<ISC00);
	EIMSK = (1<<INT0); // External interrupt request 0
	//DDRA = 0xff;


	sei();

}

void USART_init(){
	UCSR0A = (1<<U2X0); // multiplier på oscillator frequency
	unsigned int baud = 8;//klockan är 8Mhz
	UBRR0L = (unsigned char)(baud);
	UCSR0B = (1<<TXEN0)|(0<<RXEN0)|(0<<UCSZ02);// Recieve enabled. Character size = 8-bit
	UCSR0C = (1<<UCSZ01)|(1<<UCSZ00)|(0<<USBS0)|(0<<UMSEL00)|(0<<UMSEL01); // Character size = 8-bit, 1 stoppbit

}


/*unsigned int USART_Receive(void) {
      while(!(UCSR0A & (1<<RXC0) ))
      
            ;
      return UDR0;
}
*/

void USART_Transmit(unsigned char data){
	while(!(UCSR0A & (1<<UDRE0))) {}
	UDR0 = data;
	sensorCount = 0;
}

ISR(BADISR_vect) {
	while(1);
}

int main(void)
{

	USART_init();
	// Set prescaler to 1/1024 ((8/1024)MHz = 7812,5HZ)

    //8-bits register till counter för tidsräkning
    //Till overflowinterrupt
	TCCR0B = (1<<CS12)|(0<<CS11)|(1<<CS10);
    //TIMSK0 enablar overflowinterrupt
	TIMSK0 = (1<<TOIE0);

	TCCR1B = (1<<CS12)|(0<<CS11)|(1<<CS10);

	TCCR3B = (1<<CS32)|(0<<CS31)|(1<<CS30);
	isr_init();

	while(1){


		if(counter == 1){
			counter = 0;
			USART_Transmit(sensorCount);

		}


	}
}

