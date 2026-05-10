cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project(insane_sound_bar_dsp C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialize the Pico SDK
pico_sdk_init()

# Add executable
add_executable(isb_dsp
    main.c
    dsp_core1.c
    biquad.c
    i2c_slave_handler.c
    audio_routing.c
)

# Enable I2C, PIO, Multicore, Hardware I2C etc.
target_link_libraries(isb_dsp
    pico_stdlib
    pico_multicore
    hardware_i2c
    hardware_pio
    hardware_dma
    hardware_clocks
    hardware_irq
    hardware_sync
    hardware_adc
)

# PIO assembly
pico_generate_pio_header(isb_dsp ${CMAKE_CURRENT_LIST_DIR}/audio_i2s.pio)
pico_generate_pio_header(isb_dsp ${CMAKE_CURRENT_LIST_DIR}/audio_spdif.pio)

# Enable USB output, disable UART output (since UART pins are used by S3)
pico_enable_stdio_usb(isb_dsp 1)
pico_enable_stdio_uart(isb_dsp 0)

# Create map/bin/hex/uf2 files
pico_add_extra_outputs(isb_dsp)
