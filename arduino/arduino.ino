#include <N64Controller.h>

#define READY_PIN 7
#define WAIT_PIN 4

N64Controller c(2);

// a struct to contain packet data
struct controller_packet {
  const char MAGIC_NUMBER_LOW = 0x23;
  const char MAGIC_NUMBER_HIGH = 0xC0;
  
  char data[20];
  controller_packet(N64Controller* c) {
    data[0] = MAGIC_NUMBER_LOW;
    data[1] = MAGIC_NUMBER_HIGH;
    data[2] = c->L();
    data[3] = c->R();
    data[4] = c->Z();
    data[5] = c->D_up();
    data[6] = c->D_down();
    data[7] = c->D_left();
    data[8] = c->D_right();
    data[9] = c->axis_x();
    data[10] = c->axis_y();
    data[11] = c->A();
    data[12] = c->B();
    data[13] = c->C_up();
    data[14] = c->C_down();
    data[15] = c->C_left();
    data[16] = c->C_right();
    data[17] = c->Start();
    
    int sum = 0;
    for (int i = 2; i < 18; i++) {
      sum += ((int)data[i] == 0)? 0 : 1;
    }
    char sum_low = (int)sum & 0xFF;
    char sum_high = ((int)sum >> 8) & 0xFF;

    data[18] = sum_low;
    data[19] = sum_high;
  }
};

void setup() {
  // start up the LEDs
  pinMode(READY_PIN, OUTPUT);
  pinMode(WAIT_PIN, OUTPUT);
  digitalWrite(READY_PIN, LOW);
  digitalWrite(WAIT_PIN, HIGH);

  // begin our serial transmission
  Serial.begin(9600);
  c.begin();

  // flush the serial input buffer (just in case)
  while (Serial.available()) {
    Serial.read();
  }

  // now that we are done, disable the 'wait' LED and mark the unit as ready
  digitalWrite(WAIT_PIN, LOW);
  digitalWrite(READY_PIN, HIGH);
}

void loop() {
  // poll the controller and fetch button presses
  delay(30);  // the library currently requires the delay in the main loop
  c.update();

  // use the controller_packet struct to fetch and send data
  controller_packet packet(&c);

  // write the data contained in our packet struct
  int len = Serial.write(packet.data, 20);

  // verify that the bytes were sent
  if (len != 20) {
    // if there was an error, try to rectify it
    digitalWrite(WAIT_PIN, HIGH);
    if (len != 0) {
      int remainder = 20 - len;
      for (int i = 0; i < remainder; i++) {
        Serial.write(0);
      }
      digitalWrite(WAIT_PIN, LOW);
    }
  }

  // now, check to see if the controller sent any data -- if so, handle it, if we can
  if (Serial.available()) {
    // if the controller was disabled, it will send 'd'
    char c = Serial.read();
    if (c == 'd') {
      digitalWrite(READY_PIN, LOW);
      digitalWrite(WAIT_PIN, HIGH);
    }
    // if it was re-enabled, it will send 'r'
    else if (c == 'r') {
      digitalWrite(WAIT_PIN, LOW);
      digitalWrite(READY_PIN, HIGH);
    }
  }
}
