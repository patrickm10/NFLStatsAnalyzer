void inchwormEffect(uint8_t wait) {
    if (digitalRead(MOTION_SENSOR_PIN) == HIGH) {
        Serial.println("Motion detected!");

        // Number of lights to separate the "on" lights for each effect
        const int separation = 23;
        const int effectSpacing = separation + 10; // Distance between the start of each effect

        unsigned long startTime = millis(); // Record the start time
        while (millis() - startTime < 20000) { // Run for 20 seconds
            // Loop through the strip with the specified separation
            for (int i = 0; i < strip.numPixels() - effectSpacing * 2; i++) {
                // Turn all lights on initially
                for (int j = 0; j < strip.numPixels(); j++) {
                    strip.setPixelColor(j, LIGHT_BLUE); // Turn all lights to light blue
                }

                // First crawling effect
                for (int j = 0; j < separation; j++) {
                    if (i + j < strip.numPixels()) {
                        strip.setPixelColor(i + j, strip.Color(0, 0, 0)); // Turn off light
                    }
                }
                strip.setPixelColor(i, LIGHT_BLUE);                     // Start of first effect
                strip.setPixelColor(i + separation, LIGHT_BLUE);       // End of first effect

                // Second crawling effect
                for (int j = 0; j < separation; j++) {
                    if (i + effectSpacing + j < strip.numPixels()) {
                        strip.setPixelColor(i + effectSpacing + j, strip.Color(0, 0, 0)); // Turn off light
                    }
                }
                strip.setPixelColor(i + effectSpacing, LIGHT_BLUE);                     // Start of second effect
                strip.setPixelColor(i + effectSpacing + separation, LIGHT_BLUE);       // End of second effect

                // Third crawling effect
                for (int j = 0; j < separation; j++) {
                    if (i + effectSpacing * 2 + j < strip.numPixels()) {
                        strip.setPixelColor(i + effectSpacing * 2 + j, strip.Color(0, 0, 0)); // Turn off light
                    }
                }
                strip.setPixelColor(i + effectSpacing * 2, LIGHT_BLUE);                     // Start of third effect
                strip.setPixelColor(i + effectSpacing * 2 + separation, LIGHT_BLUE);       // End of third effect

                strip.show();
                delay(wait); // Delay to control the speed of the effect
            }
        }
    }
}
