#include <unity.h>
#include "volume_mapper.h"

void setUp(void) {
}

void tearDown(void) {
}

void test_volume_min() {
    TEST_ASSERT_EQUAL_UINT8(0, VolumeMapper::map_volume(0));
}

void test_volume_max() {
    TEST_ASSERT_EQUAL_UINT8(100, VolumeMapper::map_volume(127));
}

void test_volume_mid() {
    // 127/2 = 63.5 -> 63
    // (63 * 100) / 127 = 49
    TEST_ASSERT_EQUAL_UINT8(49, VolumeMapper::map_volume(63));

    // 64 -> (64 * 100) / 127 = 50
    TEST_ASSERT_EQUAL_UINT8(50, VolumeMapper::map_volume(64));
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_volume_min);
    RUN_TEST(test_volume_max);
    RUN_TEST(test_volume_mid);
    return UNITY_END();
}

#ifdef ARDUINO
#include <Arduino.h>
void setup() {
    main(0, NULL);
}
void loop() {}
#endif
