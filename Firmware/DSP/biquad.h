#ifndef BIQUAD_H
#define BIQUAD_H

#include <stdint.h>

typedef struct {
    float b0, b1, b2, a1, a2;
    float z1, z2;
} biquad_t;

void biquad_init_lp(biquad_t *bq, float fc, float fs, float q);
void biquad_init_hp(biquad_t *bq, float fc, float fs, float q);
void biquad_init_peaking(biquad_t *bq, float fc, float fs, float gain_db, float q);
float biquad_process(biquad_t *bq, float in);

// Crossovers
typedef struct {
    biquad_t bq1;
    biquad_t bq2;
} filter_4th_order_t;

void filter_init_bw4_hp(filter_4th_order_t *f, float fc, float fs);
void filter_init_lr4_lp(filter_4th_order_t *f, float fc, float fs);
void filter_init_lr4_hp(filter_4th_order_t *f, float fc, float fs);
float filter_process_4th_order(filter_4th_order_t *f, float in);

#endif // BIQUAD_H
