#include <iostream>
#include <vector>
#include <cmath>
#include "lodepng.h"

bool generate_signal_image() {
    const int width = 60;
    const int height = 60;

    std::vector<unsigned char> image(width * height, 0);

    // 2. Draw a Grey Grid (Value: 200)
    for(int y = 0; y < height; y++) {
        for(int x = 0; x < width; x++) {
            if (x % 50 == 0 || y % 50 == 0) {
                image[y * width + x] = 200; // Grey grid lines
            }
        }
    }

    // 3. Draw the Black Signal (Value: 0)
    for(int x = 0; x < width; x++) {
        double t = (double)x / width;
        double signalValue = sin(t * 8.0 * 3.14159); 
        int y = (int)((signalValue + 1.0) * (height / 2.0));

        if(y >= 0 && y < height) {
            image[y * width + x] = 0; // Black signal line
        }
    }

    // 4. Encode as Greyscale
    // LCT_GREY tells LodePNG that each pixel is exactly 1 byte (8-bit)
    unsigned error = lodepng::encode("signal_greyscale.png", image, width, height, LCT_GREY, 8);

    if(error) {
        std::cout << "PNG Encoding Error: " << lodepng_error_text(error) << std::endl;
    } else {
        std::cout << "Greyscale signal saved to signal_greyscale.png" << std::endl;
    }

    return 0;
}
