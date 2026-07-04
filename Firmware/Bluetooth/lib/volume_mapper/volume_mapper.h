#pragma once
#include <stdint.h>

class VolumeMapper {
public:
    static uint8_t map_volume(int volume) {
        // volume is 0-127, map to 0-100
        return (uint8_t)((volume * 100) / 127);
    }
};
