#ifndef AUDIO_ROUTING_H
#define AUDIO_ROUTING_H

#include <stdint.h>
#include <stdbool.h>

void audio_routing_init(void);
void audio_routing_set_input(uint8_t input_sel);
bool audio_routing_get_sample(int32_t *left, int32_t *right);
void audio_routing_put_sample(int32_t out_mid_l, int32_t out_mid_r,
                              int32_t out_high_l, int32_t out_high_r,
                              int32_t out_sub);

#endif // AUDIO_ROUTING_H
