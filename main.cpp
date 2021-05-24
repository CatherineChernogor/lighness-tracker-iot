#include "mbed.h"
#include <cstdio>
#include <string>

#define LED1 PB_3
#define SIG PA_4

#define TX PA_9
#define RX PA_10
#define BAUDRATE 115200

#define RS PA_8
#define E PA_13
#define D4 PB_11
#define D5 PB_10
#define D6 PB_1
#define D7 PB_0

static DigitalOut led(LED1);
static AnalogIn sig(SIG);

static DigitalOut rs(RS, 0);
static DigitalOut e(E, 0);
static DigitalOut d4(D4, 0);
static DigitalOut d5(D5, 0);
static DigitalOut d6(D6, 0);
static DigitalOut d7(D7, 0);

static UnbufferedSerial uart(TX, RX, BAUDRATE);
FileHandle *mbed::mbed_override_console(int fd) { return &uart; }

void send(bool isCommand, uint8_t data) {
  rs.write(isCommand ? 0 : 1);
  ThisThread::sleep_for(5ms);

  d7.write((data >> 7) & 1);
  d6.write((data >> 6) & 1);
  d5.write((data >> 5) & 1);
  d4.write((data >> 4) & 1);

  e.write(1);
  ThisThread::sleep_for(5ms);
  e.write(0);
  ThisThread::sleep_for(5ms);

  d7.write((data >> 3) & 1);
  d6.write((data >> 2) & 1);
  d5.write((data >> 1) & 1);
  d4.write((data >> 0) & 1);

  e.write(1);
  ThisThread::sleep_for(5ms);
  e.write(0);
  ThisThread::sleep_for(5ms);
}

void sendCommand(uint8_t cmd) { send(true, cmd); }
void sendChar(const char chr) { send(false, (uint8_t)chr); }
void sendString(const char *str) {
  while (*str != '\0') {
    sendChar(*str);
    str++;
  }
}

// main() runs in its own thread in the OS
int main() {
  bool canSend = false;
  char key[10] = "Send key";
  char symbol;
  int i = 0;

  sendCommand(0b00110000); // data length, 4-bit interface
  sendCommand(0b00000010); // Cursor home
  sendCommand(0b00001100); // Display on/off control
  sendCommand(0b00000001); // Clear display

  sendCommand(0b10000000); // Write CGRAM or DDRAM
  sendString("test lcd");
  char ssig[10];
  while (true) {

    int signal = sig.read_u16();

    sprintf(ssig, "%d", signal);
    sendCommand(0b00000001); // Clear display
    sendString(ssig);

    if (uart.readable()) {
      uart.read(&symbol, 1);

      if (symbol == '~') {
        printf("Elka\r\n");
        ThisThread::sleep_for(500ms);
        canSend = true;
      } else if (canSend && symbol == '&') {
        printf("%d\r\n", signal);
        ThisThread::sleep_for(500ms);
      } else {
        printf("Something wrong\r\n");
      }
    }

    led = !led;
    ThisThread::sleep_for(500ms);
  }
}
