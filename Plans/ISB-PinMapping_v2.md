# Insane Sound Bar - Pin Mapping

| IC Name | Pin | Bezeichnung | Funktion | Geht zu | Kommentar |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **U3 S3 (Master)** | EN | EN | Reset | EN Switch | PullUp 10kohm |
| **U3 S3 (Master)** | GPIO0 | BOOT | BOOT | BOOT Switch | PullUp 10kohm |
| **U3 S3 (Master)** | GPIO1 | IN_IR | IR Receiver | TSOP4838 (Pin 1) | Für TV-Remote Learning |
| **U3 S3 (Master)** | GPIO4 | UART_TX_DSP | UART TX | QSPI_SD3 (U4 RP) |  |
| **U3 S3 (Master)** | GPIO5 | UART_RX_DSP | UART RX | QSPI_SD2 (U4 RP) |  |
| **U3 S3 (Master)** | GPIO6 | UART_TX_SUB | UART TX | RXD0 (U1 SUB) | 33ohm |
| **U3 S3 (Master)** | GPIO7 | UART_RX_SUB | UART RX | TXD0 (U1 SUB) |  |
| **U3 S3 (Master)** | GPIO8 | I2C_SDA | I2C | I2C Bus | PullUp 2kohm |
| **U3 S3 (Master)** | GPIO9 | I2C_SCL | I2C | I2C Bus | PullUp 2kohm |
| **U3 S3 (Master)** | GPIO10 | UART_TX_BT | UART TX | RXD0 (U2 BT) | 33ohm |
| **U3 S3 (Master)** | GPIO11 | UART_RX_BT | UART RX | TXD0 (U2 BT) |  |
| **U3 S3 (Master)** | GPIO12 | FAULT_H | IN | 3: FAULTZ (U9 TPAH) | PullUp 100kohm |
| **U3 S3 (Master)** | GPIO13 | FAULT_M | IN | 3: FAULTZ (U8 TPAM) | PullUp 100kohm |
| **U3 S3 (Master)** | GPIO14 | DSP_EN | OUT | RUN (U4 RP) |  |
| **U3 S3 (Master)** | GPIO15 | DSP_BOOT | OUT | QSPI_SS (U4 RP) |  |
| **U3 S3 (Master)** | GPIO16 | INT_DSP | Interrupt IN | GPIO2 (U4 RP) | 330ohm |
| **U3 S3 (Master)** | GPIO17 | INT_BT | Interrupt IN | IO23 (U2 BT) | 330ohm |
| **U3 S3 (Master)** | GPIO18 | INT_SUB | Interrupt IN | IO23 (U1 SUB) | 330ohm |
| **U3 S3 (Master)** | GPIO19 | USB_D- | USB | D7 USBLC6 (Pin 3) |  |
| **U3 S3 (Master)** | GPIO20 | USB_D+ | USB | D7 USBLC6 (Pin 1) |  |
| **U3 S3 (Master)** | GPIO21 | DSP_BOOTSEL | OUT | QSPI_SD1 (U4 RP) |  |
| **U3 S3 (Master)** | GPIO38 | I2S_BCLK_M | I2S OUT | GPIO10 (U4 RP) | 22ohm |
| **U3 S3 (Master)** | GPIO39 | I2S_LRCK_M | I2S OUT | GPIO11 (U4 RP) | 22ohm |
| **U3 S3 (Master)** | GPIO40 | I2S_DOUT_M | I2S OUT | GPIO12 (U4 RP) | 22ohm |
| **U3 S3 (Master)** | GPIO41 | BT_EN | OUT | EN (U2 BT) |  |
| **U3 S3 (Master)** | GPIO42 | BT_BOOT | OUT | IO0 (U2 BT) |  |
| **U3 S3 (Master)** | GPIO47 | SUB_EN | OUT | EN (U1 SUB) |  |
| **U3 S3 (Master)** | GPIO48 | SUB_BOOT | OUT | IO0 (U1 SUB) |  |
| **U4 RP (DSP)** | GPIO0 | MUTE_CTRL | OUT | 12: MUTE (U8/U9) | 33ohm |
| **U4 RP (DSP)** | GPIO1 | XSMT_CTRL | OUT | 17: XSMT (U5/U6) / 2: SDZ (U8/U9) | 33ohm |
| **U4 RP (DSP)** | GPIO2 | INT_OUT | Interrupt OUT | GPIO16 (U3 S3) |  |
| **U4 RP (DSP)** | GPIO3 | TOSLINK_IN | IN | U10 PLR237 (VOUT) |  |
| **U4 RP (DSP)** | GPIO4 | I2C_SDA | I2C | I2C Bus |  |
| **U4 RP (DSP)** | GPIO5 | I2C_SCL | I2C | I2C Bus |  |
| **U4 RP (DSP)** | GPIO6 | ADC_MCLK | Clock OUT | 7: SCKI (U7 PCM1808) | 22ohm |
| **U4 RP (DSP)** | GPIO7 | ADC_BCLK | I2S IN | 8: BCK (U7 PCM1808) | 22ohm |
| **U4 RP (DSP)** | GPIO8 | ADC_LRCK | I2S IN | 6: LRCK (U7 PCM1808) | 22ohm |
| **U4 RP (DSP)** | GPIO9 | ADC_DIN | I2S IN | 9: DOUT (U7 PCM1808) | 22ohm |
| **U4 RP (DSP)** | GPIO10 | I2S_BCLK_M | I2S IN | GPIO38 (U3 S3) |  |
| **U4 RP (DSP)** | GPIO11 | I2S_LRCK_M | I2S IN | GPIO39 (U3 S3) |  |
| **U4 RP (DSP)** | GPIO12 | I2S_DIN_M | I2S IN | GPIO40 (U3 S3) |  |
| **U4 RP (DSP)** | GPIO13 | I2S_BCLK_BT | I2S IN | IO26 (U2 BT) |  |
| **U4 RP (DSP)** | GPIO14 | I2S_LRCK_BT | I2S IN | IO25 (U2 BT) |  |
| **U4 RP (DSP)** | GPIO15 | I2S_DIN_BT | I2S IN | IO27 (U2 BT) |  |
| **U4 RP (DSP)** | GPIO16 | DAC_BCLK | I2S OUT | 13: BCK (U5/U6) | 22ohm |
| **U4 RP (DSP)** | GPIO17 | DAC_LRCK | I2S OUT | 15: LRCK (U5/U6) | 22ohm |
| **U4 RP (DSP)** | GPIO18 | DAC_DOUT_M | I2S OUT | 14: DIN (U5 DACM) | 22ohm |
| **U4 RP (DSP)** | GPIO19 | DAC_DOUT_H | I2S OUT | 14: DIN (U6 DACH) | 22ohm |
| **U4 RP (DSP)** | GPIO20 | I2S_BCLK_SUB | I2S OUT | IO25 (U1 SUB) | 22ohm |
| **U4 RP (DSP)** | GPIO21 | I2S_LRCK_SUB | I2S OUT | IO26 (U1 SUB) | 22ohm |
| **U4 RP (DSP)** | GPIO22 | I2S_DOUT_SUB | I2S OUT | IO27 (U1 SUB) | 22ohm |
| **U4 RP (DSP)** | QSPI_SD1 | BOOTSEL | Boot Mode | GPIO21 (U3 S3) | 33ohm |
| **U4 RP (DSP)** | QSPI_SD2 | UART_TX | UART TX | GPIO5 (U3 S3) | 33ohm |
| **U4 RP (DSP)** | QSPI_SD3 | UART_RX | UART RX | GPIO4 (U3 S3) | 33ohm |
| **U4 RP (DSP)** | QSPI_SS | BOOTR | Boot Enable | GPIO15 (U3 S3) | 33ohm, PullUp 10kohm |
| **U4 RP (DSP)** | RUN | ENR | Reset | GPIO14 (U3 S3) | 33ohm, PullUp 10kohm |
| **U1 SUB (32U)** | EN | EN | Reset | GPIO47 (U3 S3) | PullUp 10kohm |
| **U1 SUB (32U)** | IO0 | BOOT | Boot Mode | GPIO48 (U3 S3) | PullUp 10kohm |
| **U1 SUB (32U)** | IO21 | I2C_SDA | I2C | I2C Bus |  |
| **U1 SUB (32U)** | IO22 | I2C_SCL | I2C | I2C Bus |  |
| **U1 SUB (32U)** | IO23 | INT_OUT | Interrupt OUT | GPIO18 (U3 S3) |  |
| **U1 SUB (32U)** | IO25 | I2S_BCLK | I2S IN | GPIO20 (U4 RP) |  |
| **U1 SUB (32U)** | IO26 | I2S_LRCK | I2S IN | GPIO21 (U4 RP) |  |
| **U1 SUB (32U)** | IO27 | I2S_DIN | I2S IN | GPIO22 (U4 RP) |  |
| **U1 SUB (32U)** | RXD0 (3) | UART_RX | UART RX | GPIO6 (U3 S3) |  |
| **U1 SUB (32U)** | TXD0 (1) | UART_TX | UART TX | GPIO7 (U3 S3) | 33ohm |
| **U2 BT (32U)** | EN | EN | Reset | GPIO41 (U3 S3) | PullUp 10kohm |
| **U2 BT (32U)** | IO0 | BOOT | Boot Mode | GPIO42 (U3 S3) | PullUp 10kohm |
| **U2 BT (32U)** | IO21 | I2C_SDA | I2C | I2C Bus |  |
| **U2 BT (32U)** | IO22 | I2C_SCL | I2C | I2C Bus |  |
| **U2 BT (32U)** | IO23 | INT_OUT | Interrupt OUT | GPIO17 (U3 S3) |  |
| **U2 BT (32U)** | IO25 | I2S_LRCK | I2S OUT | GPIO14 (U4 RP) | 22ohm |
| **U2 BT (32U)** | IO26 | I2S_BCLK | I2S OUT | GPIO13 (U4 RP) | 22ohm |
| **U2 BT (32U)** | IO27 | I2S_DOUT | I2S OUT | GPIO15 (U4 RP) | 22ohm |
| **U2 BT (32U)** | RXD0 (3) | UART_RX | UART RX | GPIO10 (U3 S3) |  |
| **U2 BT (32U)** | TXD0 (1) | UART_TX | UART TX | GPIO11 (U3 S3) | 33ohm |
| **U7 PCM1808 (ADC)** | 6: LRCK | I2S_LRCK | I2S OUT | GPIO8 (U4 RP) | 22ohm |
| **U7 PCM1808 (ADC)** | 7: SCKI | MCLK | Clock IN | GPIO6 (U4 RP) | 22ohm |
| **U7 PCM1808 (ADC)** | 8: BCK | I2S_BCLK | I2S OUT | GPIO7 (U4 RP) | 22ohm |
| **U7 PCM1808 (ADC)** | 9: DOUT | I2S_DOUT | I2S OUT | GPIO9 (U4 RP) | 22ohm |
| **U5 DACM** | 13: BCK | I2S_BCLK | I2S IN | GPIO16 (U4 RP) |  |
| **U5 DACM** | 14: DIN | I2S_DIN | I2S IN | GPIO18 (U4 RP) |  |
| **U5 DACM** | 15: LRCK | I2S_LRCK | I2S IN | GPIO17 (U4 RP) |  |
| **U5 DACM** | 17: XSMT | XSMT | Mute IN | GPIO1 (U4 RP) |  |
| **U6 DACH** | 13: BCK | I2S_BCLK | I2S IN | GPIO16 (U4 RP) |  |
| **U6 DACH** | 14: DIN | I2S_DIN | I2S IN | GPIO19 (U4 RP) |  |
| **U6 DACH** | 15: LRCK | I2S_LRCK | I2S IN | GPIO17 (U4 RP) |  |
| **U6 DACH** | 17: XSMT | XSMT | Mute IN | GPIO1 (U4 RP) |  |
| **U8 TPAM** | 2: SDZ | SDZ | Control | GPIO1 (U4 RP) | 100k PD, 10k Series |
| **U8 TPAM** | 3: FAULTZ | FAULT | OUT | GPIO13 (U3 S3) |  |
| **U8 TPAM** | 12: MUTE | MUTE | Mute IN | GPIO0 (U4 RP) |  |
| **U9 TPAH** | 2: SDZ | SDZ | Control | GPIO1 (U4 RP) | 100k PD, 10k Series |
| **U9 TPAH** | 3: FAULTZ | FAULT | OUT | GPIO12 (U3 S3) |  |
| **U9 TPAH** | 12: MUTE | MUTE | Mute IN | GPIO0 (U4 RP) |  |
| **LED1 TSOP** | 1: OUT | OUT | IR | GPIO0 (U3 S3) |  |
| **U12 SUB_RX (32U)** | IO4 | LED | OUT | Status-LED | 330ohm serie |
| **U12 SUB_RX (32U)** | IO14 | I2S_BCLK | I2S OUT | 13: BCK (U13 DAC_SUB) | 33ohm |
| **U12 SUB_RX (32U)** | IO26 | I2S_LRCK | I2S OUT | 15: LRCK (U13 DAC_SUB) | 33ohm |
| **U12 SUB_RX (32U)** | IO27 | I2S_DIN | I2S OUT | 14: DIN (U13 DAC_SUB) | 33ohm |
| **U12 SUB_RX (32U)** | IO32 | MUTE_CTRL | OUT | 12: MUTE (U14 TPA_SUB) | 33ohm |
| **U12 SUB_RX (32U)** | IO33 | XSMT_SDZ_CTRL| OUT | 17: XSMT (U13 DAC_SUB) / 2: SDZ (U14 TPA_SUB)| 33ohm |
| **U12 SUB_RX (32U)** | IO34 | FAULT_IN | IN | 3: FAULTZ (U14 TPA_SUB) | PullUp 10kohm an 3.3V |