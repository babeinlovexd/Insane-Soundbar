# Insane Sound Bar - Pin Mapping (Final & Verified)

| IC Name | Pin | Bezeichnung | Funktion | Geht zu | Kommentar |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **U3 S3 (Master)** | EN | EN | Reset | EN Switch | PullUp 10kohm |
| **U3 S3 (Master)** | GPIO0 | BOOT | BOOT | BOOT Switch | PullUp 10kohm |
| **U3 S3 (Master)** | **GPIO4** | IN_IR | IR Receiver | TSOP4838 (Pin 1) | Pad 4 |
| **U3 S3 (Master)** | **GPIO5** | DOUT | Front LED's | WS2812 DIN | 330ohm (Pad 5) |
| **U3 S3 (Master)** | **GPIO15** | BT_BOOT | OUT | IO0 (U2 BT) | Pad 8 |
| **U3 S3 (Master)** | **GPIO16** | INT_BT | Interrupt IN | IO23 (U2 BT) | 330ohm (Pad 9) |
| **U3 S3 (Master)** | **GPIO17** | DSP_EN | OUT | RUN (U4 RP) | Pad 10 |
| **U3 S3 (Master)** | **GPIO18** | FAULT_M | IN | 3: FAULTZ (U8 TPAM) | PullUp 100kohm (Pad 11) |
| **U3 S3 (Master)** | **GPIO8** | FAULT_H | IN | 3: FAULTZ (U9 TPAH) | PullUp 100kohm (Pad 12) |
| **U3 S3 (Master)** | GPIO19 | USB_D- | USB | D7 USBLC6 (Pin 3) | (Pad 13) |
| **U3 S3 (Master)** | GPIO20 | USB_D+ | USB | D7 USBLC6 (Pin 1) | (Pad 14) |
| **U3 S3 (Master)** | **GPIO9** | I2S_DOUT_M | I2S OUT | GPIO12 (U4 RP) | 22ohm (Pad 17) |
| **U3 S3 (Master)** | **GPIO10** | I2S_LRCK_M | I2S OUT | GPIO11 (U4 RP) | 22ohm (Pad 18) |
| **U3 S3 (Master)** | **GPIO11** | I2S_BCLK_M | I2S OUT | GPIO10 (U4 RP) | 22ohm (Pad 19) |
| **U3 S3 (Master)** | **GPIO12** | I2C_SDA | I2C | I2C Bus | PullUp 2kohm (Pad 20) |
| **U3 S3 (Master)** | **GPIO13** | I2C_SCL | I2C | I2C Bus | PullUp 2kohm (Pad 21) |
| **U3 S3 (Master)** | **GPIO14** | INT_DSP | Interrupt IN | GPIO5 (U4 RP) | 330ohm (Pad 22) |
| **U3 S3 (Master)** | **GPIO21** | DSP_BOOT | OUT | QSPI_SS (U4 RP) | Pad 23 |
| **U3 S3 (Master)** | **GPIO47** | DSP_BOOTSEL | OUT | QSPI_SD1 (U4 RP) | Pad 24 |
| **U3 S3 (Master)** | **GPIO48** | UART_RX_DSP | UART RX | QSPI_SD2 (U4 RP) | Pad 25 (Cross: an TX RP) |
| **U3 S3 (Master)** | **GPIO38** | UART_TX_DSP | UART TX | QSPI_SD3 (U4 RP) | Pad 31 (Cross: an RX RP) |
| **U3 S3 (Master)** | **GPIO39** | SUB_BOOT | OUT | IO0 (U1 SUB) | Pad 32 |
| **U3 S3 (Master)** | **GPIO40** | BT_EN | OUT | EN (U2 BT) | Pad 33 |
| **U3 S3 (Master)** | **GPIO41** | SUB_EN | OUT | EN (U1 SUB) | Pad 34 |
| **U3 S3 (Master)** | **GPIO42** | INT_SUB | Interrupt IN | IO23 (U1 SUB) | 330ohm (Pad 35) |
| **U3 S3 (Master)** | **GPIO43** | UART_TX_SUB | UART TX | RXD0 (U1 SUB) | Pad 36 (Cross: an RX SUB) |
| **U3 S3 (Master)** | **GPIO44** | UART_RX_SUB | UART RX | TXD0 (U1 SUB) | Pad 37 (Cross: an TX SUB) |
| **U3 S3 (Master)** | **GPIO2** | UART_TX_BT | UART TX | RXD0 (U2 BT) | Pad 38 (Cross: an RX BT) |
| **U3 S3 (Master)** | **GPIO1** | UART_RX_BT | UART RX | TXD0 (U2 BT) | Pad 39 (Cross: an TX BT) |
| **U4 RP (DSP)** | GPIO0 | I2C_SDA | I2C | I2C Bus | |
| **U4 RP (DSP)** | GPIO1 | I2C_SCL | I2C | I2C Bus | |
| **U4 RP (DSP)** | GPIO2 | I2S_DIN_BT | I2S IN | IO21 (U2 BT) | |
| **U4 RP (DSP)** | GPIO3 | I2S_BCLK_BT | I2S IN | IO19 (U2 BT) | |
| **U4 RP (DSP)** | GPIO4 | I2S_LRCK_BT | I2S IN | IO18 (U2 BT) | |
| **U4 RP (DSP)** | GPIO5 | INT_OUT | Interrupt OUT | **GPIO14 (U3 S3)** | |
| **U4 RP (DSP)** | GPIO6 | TOSLINK_IN | IN | U10 PLR237 (VOUT) | |
| **U4 RP (DSP)** | GPIO7 | ADC_DIN | I2S IN | 9: DOUT (U7 PCM1808) | 22ohm |
| **U4 RP (DSP)** | GPIO8 | ADC_BCLK | I2S IN | 8: BCK (U7 PCM1808) | 22ohm |
| **U4 RP (DSP)** | GPIO9 | ADC_LRCK | I2S IN | 6: LRCK (U7 PCM1808) | 22ohm |
| **U4 RP (DSP)** | GPIO10 | I2S_BCLK_M | I2S IN | **GPIO11 (U3 S3)** | |
| **U4 RP (DSP)** | GPIO11 | I2S_LRCK_M | I2S IN | **GPIO10 (U3 S3)** | |
| **U4 RP (DSP)** | GPIO12 | I2S_DIN_M | I2S IN | **GPIO9 (U3 S3)** | |
| **U4 RP (DSP)** | GPIO13 | ADC_MCLK | Clock OUT | 7: SCKI (U7 PCM1808) | 22ohm |
| **U4 RP (DSP)** | GPIO14 | XSMT_CTRL | OUT | 17: XSMT (U5/U6) / 2: SDZ (U8/U9) | 33ohm |
| **U4 RP (DSP)** | GPIO15 | DAC_DOUT_H | I2S OUT | 14: DIN (U6 DACH) | 22ohm |
| **U4 RP (DSP)** | GPIO16 | DAC_BCLK | I2S OUT | 13: BCK (U5/U6) | 22ohm |
| **U4 RP (DSP)** | GPIO17 | DAC_LRCK | I2S OUT | 15: LRCK (U5/U6) | 22ohm |
| **U4 RP (DSP)** | GPIO18 | MUTE_CTRL | OUT | 12: MUTE (U8/U9) | 33ohm |
| **U4 RP (DSP)** | GPIO19 | DAC_DOUT_M | I2S OUT | 14: DIN (U5 DACM) | 22ohm |
| **U4 RP (DSP)** | GPIO20 | I2S_BCLK_SUB | I2S OUT | IO27 (U1 SUB) | 22ohm |
| **U4 RP (DSP)** | GPIO21 | I2S_LRCK_SUB | I2S OUT | IO26 (U1 SUB) | 22ohm |
| **U4 RP (DSP)** | GPIO22 | I2S_DOUT_SUB | I2S OUT | IO25 (U1 SUB) | 22ohm |
| **U4 RP (DSP)** | QSPI_SD1 | BOOTSEL | Boot Mode | **GPIO47 (U3 S3)** | 33ohm |
| **U4 RP (DSP)** | QSPI_SD2 | UART_TX | UART TX | **GPIO48 (U3 S3)** | 33ohm (Cross) |
| **U4 RP (DSP)** | QSPI_SD3 | UART_RX | UART RX | **GPIO38 (U3 S3)** | 33ohm (Cross) |
| **U4 RP (DSP)** | QSPI_SS | BOOTR | Boot Enable | **GPIO21 (U3 S3)** | 33ohm, PullUp 10kohm |
| **U4 RP (DSP)** | RUN | ENR | Reset | **GPIO17 (U3 S3)** | 33ohm, PullUp 10kohm |
| **U1 SUB (32U)** | EN | EN | Reset | **GPIO41 (U3 S3)** | PullUp 10kohm |
| **U1 SUB (32U)** | IO0 | BOOT | Boot Mode | **GPIO39 (U3 S3)** | PullUp 10kohm |
| **U1 SUB (32U)** | IO19 | I2C_SDA | I2C | I2C Bus | |
| **U1 SUB (32U)** | IO21 | I2C_SCL | I2C | I2C Bus | |
| **U1 SUB (32U)** | IO23 | INT_OUT | Interrupt OUT | **GPIO42 (U3 S3)** | |
| **U1 SUB (32U)** | IO25 | I2S_DIN | I2S IN | GPIO22 (U4 RP) | |
| **U1 SUB (32U)** | IO26 | I2S_LRCK | I2S IN | GPIO21 (U4 RP) | |
| **U1 SUB (32U)** | IO27 | I2S_BCLK | I2S IN | GPIO20 (U4 RP) | |
| **U1 SUB (32U)** | RXD0 (3) | UART_RX | UART RX | **GPIO43 (U3 S3)** | (Cross) |
| **U1 SUB (32U)** | TXD0 (1) | UART_TX | UART TX | **GPIO44 (U3 S3)** | 33ohm (Cross) |
| **U2 BT (32U)** | EN | EN | Reset | **GPIO40 (U3 S3)** | PullUp 10kohm |
| **U2 BT (32U)** | IO0 | BOOT | Boot Mode | **GPIO15 (U3 S3)** | PullUp 10kohm |
| **U2 BT (32U)** | IO16 | I2C_SDA | I2C | I2C Bus | |
| **U2 BT (32U)** | IO17 | I2C_SCL | I2C | I2C Bus | |
| **U2 BT (32U)** | IO18 | I2S_LRCK | I2S OUT | GPIO4 (U4 RP) | 22ohm |
| **U2 BT (32U)** | IO19 | I2S_BCLK | I2S OUT | GPIO3 (U4 RP) | 22ohm |
| **U2 BT (32U)** | IO21 | I2S_DOUT | I2S OUT | GPIO2 (U4 RP) | 22ohm |
| **U2 BT (32U)** | IO23 | INT_OUT | Interrupt OUT | **GPIO16 (U3 S3)** | |
| **U2 BT (32U)** | RXD0 (3) | UART_RX | UART RX | **GPIO2 (U3 S3)** | (Cross) |
| **U2 BT (32U)** | TXD0 (1) | UART_TX | UART TX | **GPIO1 (U3 S3)** | 33ohm (Cross) |
| **U7 PCM1808 (ADC)** | 6: LRCK | I2S_LRCK | I2S OUT | GPIO9 (U4 RP) | 22ohm |
| **U7 PCM1808 (ADC)** | 7: SCKI | MCLK | Clock IN | GPIO13 (U4 RP) | 22ohm |
| **U7 PCM1808 (ADC)** | 8: BCK | I2S_BCLK | I2S OUT | GPIO8 (U4 RP) | 22ohm |
| **U7 PCM1808 (ADC)** | 9: DOUT | I2S_DOUT | I2S OUT | GPIO7 (U4 RP) | 22ohm |
| **U5 DACM** | 13: BCK | I2S_BCLK | I2S IN | GPIO16 (U4 RP) | |
| **U5 DACM** | 14: DIN | I2S_DIN | I2S IN | GPIO19 (U4 RP) | |
| **U5 DACM** | 15: LRCK | I2S_LRCK | I2S IN | GPIO17 (U4 RP) | |
| **U5 DACM** | 17: XSMT | XSMT | Mute IN | GPIO14 (U4 RP) | |
| **U6 DACH** | 13: BCK | I2S_BCLK | I2S IN | GPIO16 (U4 RP) | |
| **U6 DACH** | 14: DIN | I2S_DIN | I2S IN | GPIO15 (U4 RP) | |
| **U6 DACH** | 15: LRCK | I2S_LRCK | I2S IN | GPIO17 (U4 RP) | |
| **U6 DACH** | 17: XSMT | XSMT | Mute IN | GPIO14 (U4 RP) | |
| **U8 TPAM** | 2: SDZ | SDZ | Control | GPIO14 (U4 RP) | 100k PD, 10k Series |
| **U8 TPAM** | 3: FAULTZ | FAULT | OUT | **GPIO18 (U3 S3)** | |
| **U8 TPAM** | 12: MUTE | MUTE | Mute IN | GPIO18 (U4 RP) | |
| **U9 TPAH** | 2: SDZ | SDZ | Control | GPIO14 (U4 RP) | 100k PD, 10k Series |
| **U9 TPAH** | 3: FAULTZ | FAULT | OUT | **GPIO8 (U3 S3)** | |
| **U9 TPAH** | 12: MUTE | MUTE | Mute IN | GPIO18 (U4 RP) | |
| **LED1 TSOP** | 1: OUT | OUT | IR | **GPIO4 (U3 S3)** | |
| **U12 SUB_RX (32U)** | IO4 | LED | OUT | Status-LED | 330ohm serie |
| **U12 SUB_RX (32U)** | IO14 | I2S_BCLK | I2S OUT | 13: BCK (U13 DAC_SUB) | 33ohm |
| **U12 SUB_RX (32U)** | IO26 | I2S_LRCK | I2S OUT | 15: LRCK (U13 DAC_SUB) | 33ohm |
| **U12 SUB_RX (32U)** | IO27 | I2S_DIN | I2S OUT | 14: DIN (U13 DAC_SUB) | 33ohm |
| **U12 SUB_RX (32U)** | IO32 | MUTE_CTRL | OUT | 12: MUTE (U14 TPA_SUB) | 33ohm |
| **U12 SUB_RX (32U)** | IO33 | XSMT_SDZ_CTRL| OUT | 17: XSMT (U13 DAC_SUB) / 2: SDZ (U14 TPA_SUB)| 33ohm |
| **U12 SUB_RX (32U)** | IO34 | FAULT_IN | IN | 3: FAULTZ (U14 TPA_SUB) | PullUp 10kohm an 3.3V |