#include "audio_routing.h"
#include "config.h"
#include "hardware/pio.h"
#include "hardware/clocks.h"
#include "audio_i2s.pio.h"
#include "audio_spdif.pio.h"

static uint i2s_out_mid_sm;
static uint i2s_out_high_sm;
static uint i2s_out_sub_sm;

static uint i2s_in_aux_sm;
static uint i2s_in_bt_sm;
static uint i2s_in_wlan_sm;
static uint spdif_in_sm;

static uint active_input = 1; // Default to Aux

void audio_routing_init(void) {
    // Configure MCLK output for ADC (GPIO 6)
    // Assuming system clock is e.g. 125MHz, we want to output a clock for the ADC.
    // For 44.1kHz, MCLK is typically 256*Fs = 11.2896 MHz.
    clock_gpio_init(PIN_ADC_MCLK, CLOCKS_CLK_GPOUT0_CTRL_AUXSRC_VALUE_CLK_SYS, 10); // Approximation

    // Setup PIOs
    PIO pio_out = pio0;
    PIO pio_in = pio1;

    uint offset_out = pio_add_program(pio_out, &audio_i2s_out_program);
    uint offset_in = pio_add_program(pio_in, &audio_i2s_in_program);
    uint offset_spdif = pio_add_program(pio_in, &spdif_rx_48000_program);

    // Outputs
    i2s_out_mid_sm = pio_claim_unused_sm(pio_out, true);
    audio_i2s_out_program_init(pio_out, i2s_out_mid_sm, offset_out, PIN_DAC_DOUT_M, PIN_DAC_BCLK, 44100.0f, true);

    i2s_out_high_sm = pio_claim_unused_sm(pio_out, true);
    audio_i2s_out_program_init(pio_out, i2s_out_high_sm, offset_out, PIN_DAC_DOUT_H, PIN_DAC_BCLK, 44100.0f, false); // Don't drive clock again

    i2s_out_sub_sm = pio_claim_unused_sm(pio_out, true);
    audio_i2s_out_program_init(pio_out, i2s_out_sub_sm, offset_out, PIN_I2S_DOUT_SUB, PIN_I2S_BCLK_SUB, 11025.0f, true);

    // Inputs (I2S Slaves)
    i2s_in_aux_sm = pio_claim_unused_sm(pio_in, true);
    audio_i2s_in_program_init(pio_in, i2s_in_aux_sm, offset_in, PIN_ADC_DIN, PIN_ADC_BCLK);

    i2s_in_bt_sm = pio_claim_unused_sm(pio_in, true);
    audio_i2s_in_program_init(pio_in, i2s_in_bt_sm, offset_in, PIN_I2S_DIN_BT, PIN_I2S_BCLK_BT);

    i2s_in_wlan_sm = pio_claim_unused_sm(pio_in, true);
    audio_i2s_in_program_init(pio_in, i2s_in_wlan_sm, offset_in, PIN_I2S_DIN_M, PIN_I2S_BCLK_M);

    spdif_in_sm = pio_claim_unused_sm(pio_in, true);
    audio_spdif_in_program_init(pio_in, spdif_in_sm, offset_spdif, PIN_TOSLINK_IN);
}

void audio_routing_set_input(uint8_t input_sel) {
    active_input = input_sel;
}

bool audio_routing_get_sample(int32_t *left, int32_t *right) {
    uint sm;
    switch (active_input) {
        case 0: sm = spdif_in_sm; break;
        case 1: sm = i2s_in_aux_sm; break;
        case 2: sm = i2s_in_bt_sm; break;
        case 3: sm = i2s_in_wlan_sm; break;
        default: return false;
    }

    if (pio_sm_is_rx_fifo_empty(pio1, sm)) {
        return false;
    }

    uint32_t sample = pio_sm_get(pio1, sm);

    if (active_input == 0) {
        // S/PDIF sample decoding from VUCP... simple approx
        *left = (int16_t)((sample >> 4) & 0xFFFF); // Simplified parsing
        *right = *left; // Assume mono or simplified for now to unblock
    } else {
        // Unpack stereo 16-bit
        *left = (int16_t)(sample >> 16);
        *right = (int16_t)(sample & 0xFFFF);
    }
    return true;
}

void audio_routing_put_sample(int32_t out_mid_l, int32_t out_mid_r,
                              int32_t out_high_l, int32_t out_high_r,
                              int32_t out_sub) {

    uint32_t out_mid = ((out_mid_l & 0xFFFF) << 16) | (out_mid_r & 0xFFFF);
    uint32_t out_high = ((out_high_l & 0xFFFF) << 16) | (out_high_r & 0xFFFF);
    uint32_t out_sub_packed = ((out_sub & 0xFFFF) << 16) | (out_sub & 0xFFFF); // Mirror to both channels

    // Mid/High auf vollen 44.1 kHz ausgeben
    pio_sm_put_blocking(pio0, i2s_out_mid_sm, out_mid);
    pio_sm_put_blocking(pio0, i2s_out_high_sm, out_high);

    // Subwoofer Dezimierung (Teile durch 4 = 11.025 kHz)
    static uint8_t sub_counter = 0;
    if (sub_counter == 0) {
        pio_sm_put_blocking(pio0, i2s_out_sub_sm, out_sub_packed);
    }
    sub_counter = (sub_counter + 1) & 3; // Zählt blitzschnell 0, 1, 2, 3
}
