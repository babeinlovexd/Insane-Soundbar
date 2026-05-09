#ifndef I2C_REGISTERS_H
#define I2C_REGISTERS_H

#include <stdint.h>

// I2C Register Map for RP2354 (Audio DSP)
#define REG_VOL_MASTER     0x01 // W: 0-100 %
#define REG_MUTE_CTRL      0x02 // W: 0 / 1 (1 = mute system)
#define REG_INPUT_SEL      0x03 // W: 0-3 (0:Toslink, 1:Aux, 2:BT, 3:WLAN)

// EQ Bands
#define REG_EQ_B1          0x10 // W: Bass (10 = 0dB)
#define REG_EQ_B2          0x11 // W: Low-Mid (10 = 0dB)
#define REG_EQ_B3          0x12 // W: Mid (10 = 0dB)
#define REG_EQ_B4          0x13 // W: High-Mid (10 = 0dB)
#define REG_EQ_B5          0x14 // W: High (10 = 0dB)

// Trims
#define REG_TRIM_SUB       0x20 // W: Subwoofer Trim (0-20, 10=0dB)
#define REG_TRIM_MID       0x21 // W: Mid Trim (0-20, 10=0dB)
#define REG_TRIM_HIGH      0x22 // W: High Trim (0-20, 10=0dB)

// Crossovers
#define REG_XOVER_SUB_LP   0x30 // W: Subwoofer Low-pass (Hz, 50-255)
#define REG_XOVER_SAT_HP   0x31 // W: Satellite High-pass (Hz, 50-255)
#define REG_XOVER_MID_LP   0x32 // W: Mid Low-pass (*100 Hz, 35=3500)
#define REG_XOVER_HIGH_HP  0x33 // W: High High-pass (*100 Hz, 35=3500)

// System Status
#define REG_SYS_STATUS     0xFF // R: 0=OK, >0 Error Code

// Global state structure
typedef struct {
    uint8_t vol_master;
    uint8_t mute_ctrl;
    uint8_t input_sel;
    uint8_t eq_b1;
    uint8_t eq_b2;
    uint8_t eq_b3;
    uint8_t eq_b4;
    uint8_t eq_b5;
    uint8_t trim_sub;
    uint8_t trim_mid;
    uint8_t trim_high;
    uint8_t xover_sub_lp;
    uint8_t xover_sat_hp;
    uint8_t xover_mid_lp;
    uint8_t xover_high_hp;
    uint8_t sys_status;

    // Internal flags
    volatile bool registers_updated;
} dsp_state_t;

extern dsp_state_t g_dsp_state;

#endif // I2C_REGISTERS_H
