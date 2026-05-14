#ifndef CONFIG_H
#define CONFIG_H

// --- Pin Definitions (RP2354) ---

// System & Control
#define PIN_MUTE_CTRL      18
#define PIN_XSMT_CTRL      14
#define PIN_INT_OUT        5
#define PIN_I2C_SDA        0
#define PIN_I2C_SCL        1

// Audio Inputs (RX)
#define PIN_TOSLINK_IN     6

#define PIN_ADC_MCLK       13
#define PIN_ADC_BCLK       8
#define PIN_ADC_LRCK       9
#define PIN_ADC_DIN        7

#define PIN_I2S_BCLK_M     10
#define PIN_I2S_LRCK_M     11
#define PIN_I2S_DIN_M      12

#define PIN_I2S_BCLK_BT    3
#define PIN_I2S_LRCK_BT    4
#define PIN_I2S_DIN_BT     2

// Audio Outputs (TX)
#define PIN_DAC_BCLK       16
#define PIN_DAC_LRCK       17
#define PIN_DAC_DOUT_M     19
#define PIN_DAC_DOUT_H     15

#define PIN_I2S_BCLK_SUB   20
#define PIN_I2S_LRCK_SUB   21
#define PIN_I2S_DOUT_SUB   22

// I2C Address
#define DSP_I2C_ADDR       0x20

#endif // CONFIG_H
