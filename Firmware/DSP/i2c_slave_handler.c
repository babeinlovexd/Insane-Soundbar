#include "i2c_slave_handler.h"
#include "hardware/i2c.h"
#include "hardware/irq.h"
#include "pico/stdlib.h"
#include "config.h"
#include "i2c_registers.h"

// Define I2C instance
#define I2C_PORT i2c0

static uint8_t active_register = 0;
static bool reg_set = false;

static void i2c_slave_handler() {
    uint32_t status = i2c_get_hw(I2C_PORT)->intr_stat;

    // Read request
    if (status & I2C_IC_INTR_STAT_R_RD_REQ_BITS) {
        uint8_t val = 0;
        switch (active_register) {
            case REG_VOL_MASTER: val = g_dsp_state.vol_master; break;
            case REG_MUTE_CTRL: val = g_dsp_state.mute_ctrl; break;
            case REG_INPUT_SEL: val = g_dsp_state.input_sel; break;
            case REG_EQ_B1: val = g_dsp_state.eq_b1; break;
            case REG_EQ_B2: val = g_dsp_state.eq_b2; break;
            case REG_EQ_B3: val = g_dsp_state.eq_b3; break;
            case REG_EQ_B4: val = g_dsp_state.eq_b4; break;
            case REG_EQ_B5: val = g_dsp_state.eq_b5; break;
            case REG_TRIM_SUB: val = g_dsp_state.trim_sub; break;
            case REG_TRIM_MID: val = g_dsp_state.trim_mid; break;
            case REG_TRIM_HIGH: val = g_dsp_state.trim_high; break;
            case REG_XOVER_SUB_LP: val = g_dsp_state.xover_sub_lp; break;
            case REG_XOVER_SAT_HP: val = g_dsp_state.xover_sat_hp; break;
            case REG_XOVER_MID_LP: val = g_dsp_state.xover_mid_lp; break;
            case REG_XOVER_HIGH_HP: val = g_dsp_state.xover_high_hp; break;
            case REG_FW_VER_MAJOR: val = 1; break;
            case REG_FW_VER_MINOR: val = 0; break;
            case REG_FW_VER_PATCH: val = 0; break;
            case REG_SYS_STATUS: val = g_dsp_state.sys_status; break;
            case REG_TEMP_C: val = g_dsp_state.temp_c; break;
            default: val = 0xFF; break;
        }
        i2c_get_hw(I2C_PORT)->data_cmd = val;
        volatile uint32_t dummy_clear = i2c_get_hw(I2C_PORT)->clr_rd_req;
        (void)dummy_clear;
    }

    // Receive data
    if (status & I2C_IC_INTR_STAT_R_RX_FULL_BITS) {
        uint32_t data_cmd = i2c_get_hw(I2C_PORT)->data_cmd;
        uint8_t data = data_cmd & 0xFF;
        bool first_byte = (data_cmd & I2C_IC_DATA_CMD_FIRST_DATA_BYTE_BITS) != 0;

        if (first_byte) {
            active_register = data;
        } else {
            // Write to register
            switch (active_register) {
                case REG_VOL_MASTER: g_dsp_state.vol_master = data; break;
                case REG_MUTE_CTRL: g_dsp_state.mute_ctrl = data; break;
                case REG_INPUT_SEL: g_dsp_state.input_sel = data; break;
                case REG_EQ_B1: g_dsp_state.eq_b1 = data; break;
                case REG_EQ_B2: g_dsp_state.eq_b2 = data; break;
                case REG_EQ_B3: g_dsp_state.eq_b3 = data; break;
                case REG_EQ_B4: g_dsp_state.eq_b4 = data; break;
                case REG_EQ_B5: g_dsp_state.eq_b5 = data; break;
                case REG_TRIM_SUB: g_dsp_state.trim_sub = data; break;
                case REG_TRIM_MID: g_dsp_state.trim_mid = data; break;
                case REG_TRIM_HIGH: g_dsp_state.trim_high = data; break;
                case REG_XOVER_SUB_LP: g_dsp_state.xover_sub_lp = data; break;
                case REG_XOVER_SAT_HP: g_dsp_state.xover_sat_hp = data; break;
                case REG_XOVER_MID_LP: g_dsp_state.xover_mid_lp = data; break;
                case REG_XOVER_HIGH_HP: g_dsp_state.xover_high_hp = data; break;
            }
            g_dsp_state.registers_updated = true;
        }
    }
}

void i2c_slave_init(void) {
    i2c_init(I2C_PORT, 100 * 1000);
    i2c_set_slave_mode(I2C_PORT, true, DSP_I2C_ADDR);

    gpio_set_function(PIN_I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(PIN_I2C_SCL, GPIO_FUNC_I2C);
    gpio_pull_up(PIN_I2C_SDA);
    gpio_pull_up(PIN_I2C_SCL);

    // Enable I2C interrupts
    i2c_get_hw(I2C_PORT)->intr_mask = I2C_IC_INTR_MASK_M_RD_REQ_BITS | I2C_IC_INTR_MASK_M_RX_FULL_BITS;
    irq_set_exclusive_handler(I2C0_IRQ, i2c_slave_handler);
    irq_set_enabled(I2C0_IRQ, true);
}
