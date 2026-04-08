// PLANTASIA
// Author: Abby Wang + Claude
// Date: April 7, 2026
// Description: .ino file for detecting piezo mic trigger from the plant

// 3-Piezo Vibration → Serial Trigger
// Wiring:
//   Piezo 1 (F4) → A0 + GND
//   Piezo 2 (A4) → A1 + GND
//   Piezo 3 (C4) → A2 + GND

const int PIEZO_PINS[]  = {A0, A1, A2};
const char NOTE_NAMES[] = {'F', 'A', 'C'};
const int  NUM_PIEZOS   = 3;
const int  THRESHOLD    = 550;   // Abby: chose this threshold after fiddling around a little bit, would probably change for each person's setup
const int  COOLDOWN_MS  = 300;

unsigned long lastTrigger[NUM_PIEZOS] = {0, 0, 0};

void setup() {
  Serial.begin(9600);
}

// Abby: pretty simple for(if/else) loop for registering reading from the contact mic!
void loop() {
  String triggered = "";

  for (int i = 0; i < NUM_PIEZOS; i++) {
    int value = analogRead(PIEZO_PINS[i]);
    unsigned long now = millis();

    if (value > THRESHOLD && (now - lastTrigger[i]) > COOLDOWN_MS) {
      lastTrigger[i] = now;
      triggered += NOTE_NAMES[i];  // builds e.g. "F", "AC", "FAC"
    }
  }

  if (triggered.length() > 0) {
    Serial.println(triggered);
  }
}