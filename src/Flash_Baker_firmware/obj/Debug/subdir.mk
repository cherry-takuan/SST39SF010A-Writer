################################################################################
# MRS Version: {"version":"1.8.5","date":"2023/05/22"}
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Debug/debug.c 

OBJS += \
./Debug/debug.o 

C_DEPS += \
./Debug/debug.d 


# Each subdirectory must supply rules for building sources it contributes
Debug/%.o: ../Debug/%.c
	@	@	riscv-none-embed-gcc -march=rv32ecxw -mabi=ilp32e -msmall-data-limit=0 -msave-restore -Os -fmessage-length=0 -fsigned-char -ffunction-sections -fdata-sections -fno-common -Wunused -Wuninitialized  -g -I"C:\Users\Cherry\Nextcloud4\EEE\ROM_Writer\ROM_Writer\src\Flash_Baker_firmware\Debug" -I"C:\Users\Cherry\Nextcloud4\EEE\ROM_Writer\ROM_Writer\src\Flash_Baker_firmware\Core" -I"C:\Users\Cherry\Nextcloud4\EEE\ROM_Writer\ROM_Writer\src\Flash_Baker_firmware\User" -I"C:\Users\Cherry\Nextcloud4\EEE\ROM_Writer\ROM_Writer\src\Flash_Baker_firmware\Peripheral\inc" -std=gnu99 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -c -o "$@" "$<"
	@	@

