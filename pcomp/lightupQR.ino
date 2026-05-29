/* touch sensor == D11, LEDs == Digital PWM pins D3, D5, D6*/

const int ledPins[] = {3, 5, 6};
const int numLeds = 3;

const int touchPin = 11;

const unsigned long onTime = 30000; 
// stays on for 30 seconds after being touched
const int maxBrightness = 255;

// fades on and off
const int fadeStep = 3;
const unsigned long fadeInterval = 15;

unsigned long lastTouchTime = 0;
unsigned long lastFadeTime = 0;

int currentBrightness = 0;
int targetBrightness = 0;

bool touchDetected = false;

void setup() {

  // LED outputs
  for (int i = 0; i < numLeds; i++) {
    pinMode(ledPins[i], OUTPUT);
    analogWrite(ledPins[i], 0);
  }

  // touch input
  pinMode(touchPin, INPUT);

  Serial.begin(9600);
}

void loop() {

  readTouchSensor();

  updateLightTimer();

  updateFade();
}

void readTouchSensor() {

  static bool lastStableState = LOW;
  static unsigned long lastDebounceTime = 0;

  bool reading = digitalRead(touchPin);

  // debounce
  if (reading != lastStableState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > 30) {

    if (reading == HIGH) {

      touchDetected = true;

      // extends timer every touch
      lastTouchTime = millis();

      targetBrightness = maxBrightness;
    }
  }

  lastStableState = reading;
}

void updateLightTimer() {

  // turn off if 30s reached
  if (targetBrightness > 0 &&
      millis() - lastTouchTime >= onTime) {

    targetBrightness = 0;
  }
}

void updateFade() {

  if (millis() - lastFadeTime < fadeInterval) {
    return;
  }

  lastFadeTime = millis();

  // fade on
  if (currentBrightness < targetBrightness) {

    currentBrightness += fadeStep;

    if (currentBrightness > targetBrightness) {
      currentBrightness = targetBrightness;
    }
  }

  // fade off
  else if (currentBrightness > targetBrightness) {

    currentBrightness -= fadeStep;

    if (currentBrightness < targetBrightness) {
      currentBrightness = targetBrightness;
    }
  }

  // apply to LEDs
  for (int i = 0; i < numLeds; i++) {
    analogWrite(ledPins[i], currentBrightness);
  }
}