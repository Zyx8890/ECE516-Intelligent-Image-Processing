#include <FastLED.h>

#define NUM_LEDS 21  
#define DATA_PIN 11
#define BRIGHTNESS 60   // Slightly lower to prevent blurring in long exposure
#define DELAY 20        // Faster delay for a smoother wave

CRGB leds[NUM_LEDS];
float phase = 0.0;      // Tracks horizontal movement

void setup() {
  FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);
}

void loop() {
  // Clear the strip
  FastLED.clear();

  // Calculate "height" of the wave for this moment in time
 
  float sinVal = sin(phase); 
  
  // 3. Map -1.0 to 1.0 into 0 to 20 (our LED indices)
 
  int ledIndex = round(((sinVal + 1.0) / 2.0) * (NUM_LEDS - 1));

  // 4. Set the LED color (using a rainbow effect based on position)
  leds[ledIndex] = CHSV(phase * 20, 255, 255); 

  // 5. Display and increment phase
  FastLED.show();
  delay(DELAY);
  
  phase += 0.2; // Increase this to make the wave "wiggle" faster
}