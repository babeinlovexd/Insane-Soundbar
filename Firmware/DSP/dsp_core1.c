#include "pico/stdlib.h"
#include "pico/multicore.h"
#include "audio_routing.h"
#include "biquad.h"
#include "i2c_registers.h"
#include <math.h>

// Constants
#define FS_MAIN 44100.0f
#define FS_SUB 16000.0f
#define N_EQ_BANDS 5

// State
dsp_state_t g_dsp_state;

// Filters
filter_4th_order_t sub_lp;
filter_4th_order_t sat_hp_l, sat_hp_r;
filter_4th_order_t mid_lp_l, mid_lp_r;
filter_4th_order_t high_hp_l, high_hp_r;

filter_4th_order_t sub_subsonic;
biquad_t sub_eq_punch;

biquad_t eq_global_l[N_EQ_BANDS];
biquad_t eq_global_r[N_EQ_BANDS];

static void update_filters() {
    float sub_lp_hz = g_dsp_state.xover_sub_lp > 0 ? (float)g_dsp_state.xover_sub_lp : 120.0f;
    float sat_hp_hz = g_dsp_state.xover_sat_hp > 0 ? (float)g_dsp_state.xover_sat_hp : 95.0f;
    float mid_lp_hz = g_dsp_state.xover_mid_lp > 0 ? (float)(g_dsp_state.xover_mid_lp * 100) : 3500.0f;
    float high_hp_hz = g_dsp_state.xover_high_hp > 0 ? (float)(g_dsp_state.xover_high_hp * 100) : 3500.0f;

    // Subwoofer
    filter_init_lr4_lp(&sub_lp, sub_lp_hz, FS_MAIN); // Processing at main FS before decimation

    // Satellites
    filter_init_lr4_hp(&sat_hp_l, sat_hp_hz, FS_MAIN);
    filter_init_lr4_hp(&sat_hp_r, sat_hp_hz, FS_MAIN);

    // Mid
    filter_init_lr4_lp(&mid_lp_l, mid_lp_hz, FS_MAIN);
    filter_init_lr4_lp(&mid_lp_r, mid_lp_hz, FS_MAIN);

    // High
    filter_init_lr4_hp(&high_hp_l, high_hp_hz, FS_MAIN);
    filter_init_lr4_hp(&high_hp_r, high_hp_hz, FS_MAIN);

    // Subwoofer fixed filters
    filter_init_bw4_hp(&sub_subsonic, 26.0f, FS_MAIN);
    biquad_init_peaking(&sub_eq_punch, 40.0f, FS_MAIN, 2.5f, 1.4f);

    // Global EQ (Simplified, assuming standard bands)
    float eq_freqs[N_EQ_BANDS] = { 100.0f, 300.0f, 1000.0f, 3000.0f, 8000.0f };
    uint8_t eq_vals[N_EQ_BANDS] = {
        g_dsp_state.eq_b1, g_dsp_state.eq_b2, g_dsp_state.eq_b3,
        g_dsp_state.eq_b4, g_dsp_state.eq_b5
    };

    for (int i=0; i<N_EQ_BANDS; i++) {
        float gain = (float)(eq_vals[i] - 10); // 10 = 0dB
        biquad_init_peaking(&eq_global_l[i], eq_freqs[i], FS_MAIN, gain, 1.0f);
        biquad_init_peaking(&eq_global_r[i], eq_freqs[i], FS_MAIN, gain, 1.0f);
    }
}

static inline float apply_eq(biquad_t *eq_bank, float sample) {
    for (int i=0; i<N_EQ_BANDS; i++) {
        sample = biquad_process(&eq_bank[i], sample);
    }
    return sample;
}

void dsp_core1_entry() {
    // Initialize default state
    g_dsp_state.vol_master = 50;
    g_dsp_state.input_sel = 1; // Aux
    g_dsp_state.xover_sub_lp = 120;
    g_dsp_state.xover_sat_hp = 95;
    g_dsp_state.xover_mid_lp = 35;
    g_dsp_state.xover_high_hp = 35;
    for (int i=0; i<5; i++) {
        *(&g_dsp_state.eq_b1 + i) = 10;
    }
    g_dsp_state.trim_sub = 10;
    g_dsp_state.trim_mid = 10;
    g_dsp_state.trim_high = 10;

    update_filters();

    // Decimation state for Subwoofer (44.1kHz -> ~16kHz is complex, simplified here as drop)
    // Actually we need to output sub at 16kHz via its own I2S. Since we run main loop at 44.1,
    // the PIO for sub will consume at 16kHz.
    // For simplicity, we just put samples to sub PIO and let it block/drop if full, or we manage it properly.
    // In a real system, ASRC is needed. Here we just process and send.

    while (1) {
        if (g_dsp_state.registers_updated) {
            update_filters();
            audio_routing_set_input(g_dsp_state.input_sel);
            g_dsp_state.registers_updated = false;
        }

        int32_t in_l, in_r;
        if (audio_routing_get_sample(&in_l, &in_r)) {
            // Convert to float
            float fl = (float)in_l;
            float fr = (float)in_r;

            // Apply Master Volume (0-100)
            float vol = g_dsp_state.vol_master / 100.0f;
            fl *= vol;
            fr *= vol;

            // Global EQ
            fl = apply_eq(eq_global_l, fl);
            fr = apply_eq(eq_global_r, fr);

            // Subwoofer Channel (Mono Downmix)
            float f_sub = (fl + fr) * 0.5f;
            f_sub = filter_process_4th_order(&sub_subsonic, f_sub);
            f_sub = biquad_process(&sub_eq_punch, f_sub);
            f_sub = filter_process_4th_order(&sub_lp, f_sub);

            float sub_gain = powf(10.0f, (g_dsp_state.trim_sub - 10.0f) / 20.0f);
            f_sub *= sub_gain;

            // Satellites
            float fl_sat = filter_process_4th_order(&sat_hp_l, fl);
            float fr_sat = filter_process_4th_order(&sat_hp_r, fr);

            // Mid
            float fl_mid = filter_process_4th_order(&mid_lp_l, fl_sat);
            float fr_mid = filter_process_4th_order(&mid_lp_r, fr_sat);
            float mid_gain = powf(10.0f, (g_dsp_state.trim_mid - 10.0f) / 20.0f);
            fl_mid *= mid_gain;
            fr_mid *= mid_gain;

            // High
            float fl_high = filter_process_4th_order(&high_hp_l, fl_sat);
            float fr_high = filter_process_4th_order(&high_hp_r, fr_sat);
            float high_gain = powf(10.0f, (g_dsp_state.trim_high - 10.0f) / 20.0f);
            fl_high *= high_gain;
            fr_high *= high_gain;

            // Send out
            audio_routing_put_sample(
                (int32_t)fl_mid, (int32_t)fr_mid,
                (int32_t)fl_high, (int32_t)fr_high,
                (int32_t)f_sub
            );
        }
    }
}
