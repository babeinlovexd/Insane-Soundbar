#pragma once

#include "esphome/core/component.h"
#include "esphome/components/i2c/i2c.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/core/preferences.h"
#include "esphome/core/log.h"
#include <map>
#include <string>

// Include ESP-IDF NVS and I2S libraries
#include "nvs_flash.h"
#include "nvs.h"
#include "driver/i2s_std.h"
#include "driver/gpio.h"

// Addresses based on i2c_register_map.md
#define DSP_I2C_ADDR 0x20
#define BT_I2C_ADDR 0x21
#define SUB_I2C_ADDR 0x22

#define FAULT_H_PIN GPIO_NUM_12
#define FAULT_M_PIN GPIO_NUM_13

namespace esphome {
namespace isb_orchestrator {

class ISBOrchestrator : public Component {
 protected:
  bool learn_mode_active = false;
  std::string learn_target = "";
  std::map<uint32_t, std::string> ir_mappings;
  uint8_t current_volume = 50;
  i2c::I2CBus *i2c_bus_;
  nvs_handle_t my_handle;
  text_sensor::TextSensor *versions_sensor_{nullptr};

 public:
  void set_i2c_bus(i2c::I2CBus *bus) { i2c_bus_ = bus; }
  void set_versions_sensor(text_sensor::TextSensor *sensor) { versions_sensor_ = sensor; }

  void setup() override {
    // 1. Send MUTE to DSP immediately
    set_dsp_mute(true);

    // Initialize NVS
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
      ESP_ERROR_CHECK(nvs_flash_erase());
      err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);

    load_ir_mappings();

    // 2. Setup Fault Pins (Input, PullUp)
    gpio_config_t io_conf = {};
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pin_bit_mask = (1ULL<<FAULT_H_PIN) | (1ULL<<FAULT_M_PIN);
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.pull_up_en = GPIO_PULLUP_ENABLE;
    gpio_config(&io_conf);

    // 3. Setup I2S Audio Pipeline
    setup_i2s();

    // Check fault pins. In a real system, you'd wait/loop if low.
    if (gpio_get_level(FAULT_H_PIN) == 0 || gpio_get_level(FAULT_M_PIN) == 0) {
        ESP_LOGE("ISB_ORCH", "Fault detected on U8 or U9! Cannot Unmute safely.");
    } else {
        // Wait for I2S Sync (simulated delay, in reality wait for PLL lock / clocks stable)
        delay(500);
        // 4. Unmute DSP
        set_dsp_mute(false);
        ESP_LOGI("ISB_ORCH", "System Boot Sequence Complete. Unmuted.");
    }

    update_versions();
  }

  void setup_i2s() {
    i2s_chan_handle_t tx_chan;
    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, &tx_chan, NULL));

    i2s_std_config_t std_cfg = {
        .clk_cfg  = I2S_STD_CLK_DEFAULT_CONFIG(44100),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,    // We only need BCLK, LRCK, DOUT
            .bclk = GPIO_NUM_15,
            .ws   = GPIO_NUM_16,
            .dout = GPIO_NUM_17,
            .din  = I2S_GPIO_UNUSED,
            .invert_flags = {
                .mclk_inv = false,
                .bclk_inv = false,
                .ws_inv   = false,
            },
        },
    };

    ESP_ERROR_CHECK(i2s_channel_init_std_mode(tx_chan, &std_cfg));
    ESP_ERROR_CHECK(i2s_channel_enable(tx_chan));
    ESP_LOGI("ISB_ORCH", "I2S Master initialized on GPIOs: BCLK=15, LRCK=16, DOUT=17");
  }

  void load_ir_mappings() {
    err_t err = nvs_open("ir_storage", NVS_READWRITE, &my_handle);
    if (err != ESP_OK) return;

    size_t required_size;
    const char* keys[] = {"Vol+", "Vol-", "Mute", "Input Next"};
    for(const char* key : keys) {
        uint32_t code = 0;
        err = nvs_get_u32(my_handle, key, &code);
        if (err == ESP_OK) {
            ir_mappings[code] = std::string(key);
            ESP_LOGI("ISB_ORCH", "Loaded IR Mapping: %08X -> %s", code, key);
        }
    }
    nvs_close(my_handle);
  }

  void save_ir_mapping(uint32_t code, std::string target) {
      err_t err = nvs_open("ir_storage", NVS_READWRITE, &my_handle);
      if (err == ESP_OK) {
          nvs_set_u32(my_handle, target.c_str(), code);
          nvs_commit(my_handle);
          nvs_close(my_handle);
          ESP_LOGI("ISB_ORCH", "Saved IR Mapping to NVS: %08X -> %s", code, target.c_str());
      }
  }

  void set_dsp_mute(bool mute) {
    uint8_t data[2] = {0x02, mute ? (uint8_t)1 : (uint8_t)0};
    i2c_bus_->write(DSP_I2C_ADDR, data, 2);
    ESP_LOGD("ISB_ORCH", "Sent MUTE=%d to DSP", mute);
  }

  void set_dsp_volume(uint8_t vol_linear) {
    uint8_t vol_log = (vol_linear * vol_linear) / 100;
    current_volume = vol_log;

    uint8_t data[2] = {0x01, vol_log};
    i2c_bus_->write(DSP_I2C_ADDR, data, 2);
    ESP_LOGD("ISB_ORCH", "Sent VOL=%d (linear %d) to DSP", vol_log, vol_linear);
  }

  void handle_ir_code(uint32_t code) {
    if (learn_mode_active) {
      ESP_LOGI("ISB_ORCH", "Learned code %08X for target %s", code, learn_target.c_str());
      ir_mappings[code] = learn_target;
      save_ir_mapping(code, learn_target);
      learn_mode_active = false;
      learn_target = "";
    } else {
      auto it = ir_mappings.find(code);
      if (it != ir_mappings.end()) {
        std::string action = it->second;
        ESP_LOGI("ISB_ORCH", "Received IR %08X, Action: %s", code, action.c_str());

        if (action == "Vol+") {
          set_dsp_volume(std::min(100, current_volume + 5));
        } else if (action == "Vol-") {
          set_dsp_volume(std::max(0, current_volume - 5));
        }
      } else {
        ESP_LOGD("ISB_ORCH", "Unknown IR Code: %08X", code);
      }
    }
  }

  void enable_learn_mode(std::string target) {
    learn_mode_active = true;
    learn_target = target;
    ESP_LOGI("ISB_ORCH", "Learn Mode Activated for: %s", target.c_str());
  }

  uint8_t get_volume() { return current_volume; }

  bool is_sub_connected() {
    uint8_t reg = 0x01;
    uint8_t val = 0;
    i2c_bus_->write(SUB_I2C_ADDR, &reg, 1);
    i2c_bus_->read(SUB_I2C_ADDR, &val, 1);
    return val == 1;
  }

  bool is_bt_connected() {
    uint8_t reg = 0x01;
    uint8_t val = 0;
    i2c_bus_->write(BT_I2C_ADDR, &reg, 1);
    i2c_bus_->read(BT_I2C_ADDR, &val, 1);
    return (val == 2 || val == 3);
  }

  std::string get_slave_version(uint8_t addr) {
    uint8_t major = 0, minor = 0, patch = 0;

    uint8_t reg_major = 0xF0;
    i2c_bus_->write(addr, &reg_major, 1);
    i2c_bus_->read(addr, &major, 1);

    uint8_t reg_minor = 0xF1;
    i2c_bus_->write(addr, &reg_minor, 1);
    i2c_bus_->read(addr, &minor, 1);

    uint8_t reg_patch = 0xF2;
    i2c_bus_->write(addr, &reg_patch, 1);
    i2c_bus_->read(addr, &patch, 1);

    char buf[16];
    snprintf(buf, sizeof(buf), "%d.%d.%d", major, minor, patch);
    return std::string(buf);
  }

  void update_versions() {
    if (versions_sensor_ != nullptr) {
      std::string dsp_ver = get_slave_version(DSP_I2C_ADDR);
      std::string bt_ver = get_slave_version(BT_I2C_ADDR);
      std::string sub_ver = get_slave_version(SUB_I2C_ADDR);

      char json_buf[128];
      snprintf(json_buf, sizeof(json_buf),
               "{\"dsp\":\"%s\",\"bt\":\"%s\",\"sub\":\"%s\"}",
               dsp_ver.c_str(), bt_ver.c_str(), sub_ver.c_str());

      versions_sensor_->publish_state(json_buf);
      ESP_LOGD("ISB_ORCH", "Published versions: %s", json_buf);
    }
  }
};

} // namespace isb_orchestrator
} // namespace esphome
