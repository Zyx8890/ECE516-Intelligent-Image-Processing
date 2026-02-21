#include <FastLED.h>

#define NUM_LEDS 21  
#define DATA_PIN 11
#define BRIGHTNESS 100
#define DELAY 100  

CRGB leds[NUM_LEDS];

void setup() {
  FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);
}

void loop() {
  showH();
  delay(500);

  showE();
  delay(500);

  showL();
  delay(500);

  showL();
  delay(500);

  showO();
  delay(500);
}

void fillColor(CRGB color) {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = color;
  }
}

void showH() {
  fillColor(CRGB::Green);
  FastLED.show();
  delay(2*DELAY);

  fillColor(CRGB::Black);
  leds[10] = CRGB::Green; 
  FastLED.show();
  delay(4*DELAY);

  fillColor(CRGB::Green);
  FastLED.show();
  delay(DELAY);
}

void showE(){
  fillColor(CRGB::Green);
  FastLED.show();
  delay(2*DELAY);

  fillColor(CRGB::Black);
  leds[0]  = CRGB::Green; 
  leds[1]  = CRGB::Green; 
  leds[10] = CRGB::Green;
  leds[19] = CRGB::Green; 
  leds[20] = CRGB::Green;
  delay(5*DELAY);
}

void showL(){
  fillColor(CRGB::Green);
  FastLED.show();
  delay(2*DELAY);

  fillColor(CRGB::Black);
  leds[19] = CRGB::Green; 
  leds[20] = CRGB::Green;
  delay(5*DELAY);
}

void showO(){
  // set 3rd~19th green
  for (int i = 2; i < NUM_LEDS-2; i++) {
    leds[i] = CRGB::Green;      
  }
  FastLED.show();
  delay(DELAY);

  // 2nd~20th green
  leds[1] = CRGB::Green; 
  leds[19] = CRGB::Green;
  FastLED.show();
  delay(DELAY); 

  // 1st,2nd,20th,21th green
  leds[0] = CRGB::Green;
  leds[20] = CRGB::Green;
  for (int i = 2; i < NUM_LEDS-2; i++) {
    leds[i] = CRGB::Black;      
  }
  FastLED.show();
  delay(4*DELAY);

  // 2nd~20th green
  leds[0] = CRGB::Black;
  leds[20] = CRGB::Black;
  for (int i = 2; i < NUM_LEDS-2; i++) {
    leds[i] = CRGB::Green;      
  }
  FastLED.show();
  delay(DELAY);

  // 3rd~19th green
  leds[0] = CRGB::Black; 
  leds[20] = CRGB::Black;
  FastLED.show();
}
