/**
 * Reading of DHT22 sensor on Raspberry Pi Pico
 * Code taken and modified from: 
 * https://github.com/carolinedunn/pico-weather-station
 **/
//libraries we need
#include <stdio.h>
#include <math.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include <string.h>
// #include "hardware/i2c.h"
#include "pico/binary_info.h"

//setup for DHT
//connect DHT signal to GPIO15
const uint LED_PIN = PICO_DEFAULT_LED_PIN;
const uint DHT_PIN = 15;
const uint MAX_TIMINGS = 85;

//set humidity and temp as float
typedef struct {
    float humidity;
    float temp_celsius;
} dht_reading;

void read_from_dht(dht_reading *result);

//helper function to read from the DHT
void read_from_dht(dht_reading *result) {
    int data[5] = {0, 0, 0, 0, 0};
    uint last = 1;
    uint j = 0;

    gpio_set_dir(DHT_PIN, GPIO_OUT);
    gpio_put(DHT_PIN, 0);
    sleep_ms(20);
    //gpio_put(DHT_PIN, 1);
    //sleep_us(40);
    gpio_set_dir(DHT_PIN, GPIO_IN);

    gpio_put(LED_PIN, 1);
    for (uint i = 0; i < MAX_TIMINGS; i++) {
        uint count = 0;
        while (gpio_get(DHT_PIN) == last) {
            count++;
            sleep_us(1);
            if (count == 255) break;
        }
        last = gpio_get(DHT_PIN);
        if (count == 255) break;

        if ((i >= 4) && (i % 2 == 0)) {
            data[j / 8] <<= 1;
            if (count > 46) data[j / 8] |= 1;
            j++;
        }
    }
    gpio_put(LED_PIN, 0);

    if ((j >= 40) && (data[4] == ((data[0] + data[1] + data[2] + data[3]) & 0xFF))) {
        result->humidity = (float) ((data[0] << 8) + data[1]) / 10;
        if (result->humidity > 100) {
            result->humidity = data[0];
        }
        result->temp_celsius = (float) (((data[2] & 0x7F) << 8) + data[3]) / 10;
        if (result->temp_celsius > 125) {
            result->temp_celsius = data[2];
        }
        if (data[2] & 0x80) {
            result->temp_celsius = -result->temp_celsius;
        }
    } else {
        printf("Bad data\n");
    }
}

int main() {
    stdio_init_all(); /* USB output */
    gpio_init(LED_PIN);
    gpio_init(DHT_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    while (1) {
        dht_reading reading;
        read_from_dht(&reading);
        float celsius = reading.temp_celsius;
        printf("Humidity = %.1f%%, Temperature = %.1fC\n",
                reading.humidity, reading.temp_celsius);
        
        sleep_ms(60000); // in millis
    }
    return 0;
}