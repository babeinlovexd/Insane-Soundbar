cmake_minimum_required(VERSION 3.13)

if (COMMAND cmake_policy)
    cmake_policy(SET CMP0079 NEW)
endif()

if (NOT DEFINED ENV{PICO_SDK_PATH})
    set(PICO_SDK_PATH "${CMAKE_CURRENT_LIST_DIR}/../../pico-sdk" CACHE PATH "Path to the Raspberry Pi Pico SDK")
endif()

set(PICO_SDK_PATH "$ENV{PICO_SDK_PATH}" CACHE PATH "Path to the Raspberry Pi Pico SDK")

if (NOT EXISTS "${PICO_SDK_PATH}/pico_sdk_init.cmake")
    message(WARNING "PICO_SDK_PATH does not point to a valid Raspberry Pi Pico SDK. Set it to the correct path.")
else()
    include("${PICO_SDK_PATH}/pico_sdk_init.cmake")
endif()
