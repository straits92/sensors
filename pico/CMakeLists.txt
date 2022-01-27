cmake_minimum_required(VERSION 3.12)

include(pico_sdk_import.cmake)

project(sensorpicoDHT22)

pico_sdk_init()

add_executable(sensorpicoDHT22
        sensorpicoDHT22.c
        )
        
pico_enable_stdio_usb(sensorpicoDHT22 1)
pico_enable_stdio_uart(sensorpicoDHT22 0)

target_link_libraries(sensorpicoDHT22 pico_stdlib hardware_i2c)

pico_add_extra_outputs(sensorpicoDHT22)
