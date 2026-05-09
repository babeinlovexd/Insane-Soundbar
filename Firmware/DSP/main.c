#include "pico/stdlib.h"
#include "pico/multicore.h"
#include "config.h"
#include "i2c_registers.h"
#include "i2c_slave_handler.h"
#include "audio_routing.h"
#include "dsp_core1.h"

// Hard mute system
static void mute_system(bool mute) {
    if (mute) {
        gpio_put(PIN_MUTE_CTRL, 0); // Active LOW
        gpio_put(PIN_XSMT_CTRL, 0); // Active LOW
    } else {
        // Unmute with 50ms delay per SOW
        sleep_ms(50);
        gpio_put(PIN_MUTE_CTRL, 1);
        gpio_put(PIN_XSMT_CTRL, 1);
    }
}

int main() {
    stdio_init_all();

    // Initialize control pins
    gpio_init(PIN_MUTE_CTRL);
    gpio_set_dir(PIN_MUTE_CTRL, GPIO_OUT);

    gpio_init(PIN_XSMT_CTRL);
    gpio_set_dir(PIN_XSMT_CTRL, GPIO_OUT);

    gpio_init(PIN_INT_OUT);
    gpio_set_dir(PIN_INT_OUT, GPIO_OUT);
    gpio_put(PIN_INT_OUT, 0);

    // Initial mute (Anti-pop)
    mute_system(true);

    // Initialize subsystems
    i2c_slave_init();
    audio_routing_init();

    // Launch Core 1 (DSP Processing)
    multicore_launch_core1(dsp_core1_entry);

    // Main loop (Core 0)
    uint8_t current_input = g_dsp_state.input_sel;
    uint8_t current_mute = g_dsp_state.mute_ctrl;

    // Unmute system after successful init
    mute_system(false);

    while (1) {
        // Check for state changes from I2C
        if (g_dsp_state.mute_ctrl != current_mute) {
            current_mute = g_dsp_state.mute_ctrl;
            mute_system(current_mute == 1);
        }

        if (g_dsp_state.input_sel != current_input) {
            current_input = g_dsp_state.input_sel;

            // Hard Mute during switch
            mute_system(true);

            // Signal to DSP core 1 handled in dsp_core1.c via g_dsp_state

            // Wait for stable clock (simulated delay for stable clock acquisition)
            sleep_ms(20);

            // Unmute with 50ms delay
            mute_system(false);
        }

        // I2S/Clock error detection placeholder
        // If sync error:
        // gpio_put(PIN_INT_OUT, 1);
        // sleep_ms(5);
        // gpio_put(PIN_INT_OUT, 0);

        sleep_ms(10);
    }

    return 0;
}
