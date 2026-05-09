#include "biquad.h"
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

void biquad_init_lp(biquad_t *bq, float fc, float fs, float q) {
    float w0 = 2.0f * M_PI * fc / fs;
    float alpha = sinf(w0) / (2.0f * q);
    float cos_w0 = cosf(w0);

    float a0 = 1.0f + alpha;
    bq->b0 = ((1.0f - cos_w0) / 2.0f) / a0;
    bq->b1 = (1.0f - cos_w0) / a0;
    bq->b2 = ((1.0f - cos_w0) / 2.0f) / a0;
    bq->a1 = (-2.0f * cos_w0) / a0;
    bq->a2 = (1.0f - alpha) / a0;

    bq->z1 = 0.0f;
    bq->z2 = 0.0f;
}

void biquad_init_hp(biquad_t *bq, float fc, float fs, float q) {
    float w0 = 2.0f * M_PI * fc / fs;
    float alpha = sinf(w0) / (2.0f * q);
    float cos_w0 = cosf(w0);

    float a0 = 1.0f + alpha;
    bq->b0 = ((1.0f + cos_w0) / 2.0f) / a0;
    bq->b1 = -(1.0f + cos_w0) / a0;
    bq->b2 = ((1.0f + cos_w0) / 2.0f) / a0;
    bq->a1 = (-2.0f * cos_w0) / a0;
    bq->a2 = (1.0f - alpha) / a0;

    bq->z1 = 0.0f;
    bq->z2 = 0.0f;
}

void biquad_init_peaking(biquad_t *bq, float fc, float fs, float gain_db, float q) {
    float A = powf(10.0f, gain_db / 40.0f);
    float w0 = 2.0f * M_PI * fc / fs;
    float alpha = sinf(w0) / (2.0f * q);

    float a0 = 1.0f + alpha / A;
    bq->b0 = (1.0f + alpha * A) / a0;
    bq->b1 = (-2.0f * cosf(w0)) / a0;
    bq->b2 = (1.0f - alpha * A) / a0;
    bq->a1 = (-2.0f * cosf(w0)) / a0;
    bq->a2 = (1.0f - alpha / A) / a0;

    bq->z1 = 0.0f;
    bq->z2 = 0.0f;
}

float biquad_process(biquad_t *bq, float in) {
    float out = bq->b0 * in + bq->z1;
    bq->z1 = bq->b1 * in - bq->a1 * out + bq->z2;
    bq->z2 = bq->b2 * in - bq->a2 * out;
    return out;
}

void filter_init_bw4_hp(filter_4th_order_t *f, float fc, float fs) {
    // 4th order Butterworth requires two 2nd order sections with different Q factors
    // Q1 = 0.54119610 (1 / (2 * cos(3*pi/8)))
    // Q2 = 1.30656296 (1 / (2 * cos(pi/8)))
    biquad_init_hp(&f->bq1, fc, fs, 0.54119610f);
    biquad_init_hp(&f->bq2, fc, fs, 1.30656296f);
}

// Linkwitz-Riley 4th order is two Butterworth 2nd order in cascade
void filter_init_lr4_lp(filter_4th_order_t *f, float fc, float fs) {
    float q_butterworth = 0.70710678118f; // 1 / sqrt(2)
    biquad_init_lp(&f->bq1, fc, fs, q_butterworth);
    biquad_init_lp(&f->bq2, fc, fs, q_butterworth);
}

void filter_init_lr4_hp(filter_4th_order_t *f, float fc, float fs) {
    float q_butterworth = 0.70710678118f;
    biquad_init_hp(&f->bq1, fc, fs, q_butterworth);
    biquad_init_hp(&f->bq2, fc, fs, q_butterworth);
}

float filter_process_4th_order(filter_4th_order_t *f, float in) {
    float out1 = biquad_process(&f->bq1, in);
    return biquad_process(&f->bq2, out1);
}
