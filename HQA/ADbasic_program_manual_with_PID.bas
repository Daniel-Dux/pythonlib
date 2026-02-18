'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 2
' Initial_Processdelay           = 10000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.3.1
' Optimize                       = Yes
' Optimize_Level                 = 4
' Stacksize                      = 1000
' Info_Last_Save                 = ATI098-60  ATI098-60\labuser
'<Header End>
#include adwinpro_all.inc

#define ZERO            32768       ' Zero Volts in Adwin 16bit representation
#define N               32768       ' Max Voltage offset by ZERO

#define DIO1  1              ' DIO  Card 32
#define DIO2  2              ' DIO  Card 32
#define AIN1  3              ' AIN  Card 8/16
#define AIN2  4              ' AIN  Card 8/16
#define AOUT1 5              ' AOUT Card 8/16
#define AOUT2 6              ' AOUT Card 8/16

#define AOUTNO 16            ' Number of output channels


DIM DATA_93[8] AS Long           'AIN1 values
DIM DATA_94[8] AS Long           'AIN2 values
DIM DATA_97[AOUTNO] AS LONG      'AOut Values

'Declare PID SETTINGS Arrays
DIM DATA_98[AOUTNO] AS LONG      'PID A_In channel
DIM DATA_99[AOUTNO] AS FLOAT     'PID P
DIM DATA_100[AOUTNO] AS FLOAT    'PID I
DIM DATA_101[AOUTNO] AS FLOAT    'PID D
DIM DATA_102[AOUTNO] AS LONG     'Min AOut value
DIM DATA_103[AOUTNO] AS LONG     'Max AOut value


'Declare PID integrator and differentiator values
DIM pidn AS LONG 'Number of selected PID channels
DIM pid_error AS LONG 'Difference between target and actual voltage
DIM pid_dError AS FLOAT 'Difference times differential gain
DIM pid_lin AS FLOAT 'Proportional part of PID
DIM pid_sum[AOUTNO] AS FLOAT 'Integral part of PID
DIM pid_diff AS FLOAT 'Differential part of PID
DIM pid_prev_dError[AOUTNO] AS FLOAT

'Declare arrays for storing AIN and setting AOUT channels
DIM set_output[AOUTNO] AS LONG  ' Set values to be written to AOUTs
DIM act_values[AOUTNO] AS LONG   ' Analog values measured from AINs

DIM i AS LONG 'for loop index

INIT:
  PROCESSDELAY = 500000
  Par_11 = 0 ' Parameter to start the output
  P2_Set_Led(DIO1, 1)
  P2_Set_Led(DIO2, 1)
  P2_Set_Led(AOUT1, 1)
  P2_Set_Led(AOUT2, 1)
  P2_Start_ConvF(AIN1,0FFh)
  P2_Start_ConvF(AIN2,0FFh)

  'Set DIO channels as outputs
  P2_DigProg(DIO1, 1111b)     'Channel 0-31 as outputs
  P2_DigProg(DIO2, 1111b)     'Channel 32-63 as outputs

  '=============================================================PID SETTINGS==============================================================
  FOR i=1 TO AOUTNO
    DATA_97[i] =ZERO
    DATA_98[i] =0
    DATA_99[i] =0
    DATA_100[i]=0
    DATA_101[i]=0
    DATA_102[i]=0
    DATA_103[i]=65535
  NEXT i


  'Initialize Integrator and Difference
  FOR i=1 TO AOUTNO
    pid_sum[i]=0
    pid_prev_dError[i]=0
  NEXT i

EVENT:
  P2_Wait_EOCF(AIN1,0FFh)
  P2_Wait_EOCF(AIN2,0FFh)
  P2_READ_ADCF8(AIN1, DATA_93, 1)
  P2_READ_ADCF8(AIN2, DATA_94, 1)
  P2_Start_ConvF(AIN1,0FFh)
  P2_Start_ConvF(AIN2,0FFh)


  ' The outputs are only set if the progam_manual function is called (Par_11 is set there).
  IF (Par_11=1) THEN
    'TODO: Combine DATA_93 and 94.

    FOR i=1 TO 8
      act_values[i] = DATA_93[i]
      act_values[i+8] = DATA_94[i]
    NEXT i


    FOR i=1 TO 16
      pidn = DATA_98[i]
      if (pidn = 0) then
        'No PID active
        set_output[i]=DATA_97[i]
        pid_sum[i] = act_values[pidn]-N
        pid_prev_dError[i] = 0
      else
        'Get deviation from target voltage
        pid_error = DATA_97[i]- act_values[pidn]
        'Get proportional part
        pid_lin=DATA_99[pidn]*pid_error
        'Get integral part
        pid_sum[i] = pid_sum[i] + DATA_100[pidn]*pid_error
        'Get differential part
        pid_dError = DATA_101[pidn]* pid_error
        pid_diff = pid_dError - pid_prev_dError[i]
        pid_prev_dError[i] = pid_dError

        'Check for integral overflow
        if (pid_sum[i] > N) then pid_sum[i] = N
        if (pid_sum[i] < -N) then pid_sum[i] = -N

        set_output[i]=(pid_lin+pid_sum[i]+pid_diff) + N
      endif
      ' Check that output is within safe limits
      if (set_output[i] < DATA_102[i]) then set_output[i] = DATA_102[i]
      if (set_output[i] > DATA_103[i]) then set_output[i] = DATA_103[i]
    NEXT i


    P2_DAC8(AOUT1,set_output,1)
    P2_DAC8(AOUT2,set_output,9)
    P2_DIGOUT_LONG(DIO1,Par_91)
    P2_DIGOUT_LONG(DIO2,Par_92)

  ENDIF

FINISH:
  P2_SET_LED(DIO1,0)
  P2_SET_LED(DIO2,0)
  P2_SET_LED(AOUT1,0)
  P2_SET_LED(AOUT2,0)
  P2_SET_LED(AIN1,0)
  P2_SET_LED(AIN2,0)
