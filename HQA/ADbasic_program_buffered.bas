'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 2000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.3.1
' Optimize                       = Yes
' Optimize_Level                 = 4
' Stacksize                      = 1000
' Info_Last_Save                 = QI-ADWIN  QI-ADWIN\labuser
'<Header End>
#include adwinpro_all.inc

' Array Size Settings
' TODO: check these values in labscript_devices files
#define ZERO            32768       ' Zero Volts in Adwin 16bit representation
#define N               32768       ' Max Voltage offset by ZERO
#define MAX_EVENTS      200000      ' Max number of events that can be stored
#define MAX_PID_EVENTS  2000        ' Max number of changing the AIN channel for PID feedback to AOUT
#define MAX_TICO_EVENTS 3000        ' Max number of Digital Output events
#define A_IN_BUFFER     30000000    ' Size of Array to transmit AIN values to the runner PC
#define PIDNO           100         ' Max Number of PIDs
#define AOUTNO          16          ' Number of output channels
#define AINNO           16          ' Number of input channels

' Set Module Adresses
' TODO get or set these values from labscript ?
#define DIO1  1                         'DIO  Card 32
#define DIO2  2                         'DIO  Card 32
#define AIN1  3                         'AIN  Card 8/16
#define AIN2  4                         'AIN  Card 8/16
#define AOUT1 5                         'AOUT Card 8/16
#define AOUT2 6                         'AOUT Card 8/16

' Declare arrays for analog data from experiment control software
DIM DATA_1[MAX_EVENTS] AS LONG          'Analog time
DIM DATA_2[MAX_EVENTS] AS LONG          'Analog channel
DIM DATA_3[MAX_EVENTS] AS LONG          'Analog ouput value

' Declare arrays for PID channels for each AOUT channel
DIM DATA_4[MAX_PID_EVENTS] AS LONG      'Times for changing PID channels
DIM DATA_5[MAX_PID_EVENTS] AS LONG      'PID A_OUT channel
DIM DATA_6[MAX_PID_EVENTS] AS LONG      'PID A_In channel
DIM DATA_24[PIDNO] AS FLOAT         'PID channel for init parameters
DIM DATA_25[PIDNO] AS FLOAT         'PID P values
DIM DATA_26[PIDNO] AS FLOAT         'PID I values
DIM DATA_27[PIDNO] AS FLOAT         'PID D values
DIM DATA_28[PIDNO] AS LONG         'PID min values
DIM DATA_29[PIDNO] AS LONG         'PID max values
DIM DATA_30[MAX_PID_EVENTS] AS LONG         'PID start values

' Declare arrays for AIN Channel Timings
DIM DATA_7[AINNO] AS LONG               'Start times for channel recording
DIM DATA_8[AINNO] AS LONG               'End times for channel recording
DIM DATA_9[AINNO] AS LONG               'Gain modes for AIN channels
DIM DATA_199[A_IN_BUFFER+16] AS LONG    'Recorded Data - add padding at the end to ensure no overflow happens
DIM ain_index[AINNO] AS LONG            'Index of the data acquisition for each channel, to have the values sorted

'Declare arrays for digital data from experiment control software
DIM DATA_10[MAX_TICO_EVENTS] AS LONG    'DIO1 TiCo times
DIM DATA_11[MAX_TICO_EVENTS] AS LONG    'DIO1 digital output values
DIM DATA_20[MAX_TICO_EVENTS] AS LONG    'DIO2 TiCo times
DIM DATA_21[MAX_TICO_EVENTS] AS LONG    'DIO2 digital output values

' TO BE REMOVED IN REAL USAGE !!
DIM DATA_31[MAX_EVENTS] AS LONG ' Workload Array for testing

'Declare arrays to store TICO memory pointers
DIM PTR_TICO1[150] AS LONG
DIM PTR_TICO2[150] AS LONG

'Declare PID SETTINGS Arrays
DIM pid_P[PIDNO] AS FLOAT
DIM pid_I[PIDNO] AS FLOAT
DIM pid_D[PIDNO] AS FLOAT
DIM pid_min[PIDNO] AS LONG
DIM pid_max[PIDNO] AS LONG

'Declare PID integrator and differentiator values
DIM pidn AS LONG 'Number of selected PID channels
DIM pid_error AS LONG 'Difference between target and actual voltage
DIM pid_dError AS FLOAT 'Difference times differential gain
DIM pid_lin AS FLOAT 'Proportional part of PID
DIM pid_sum[AOUTNO] AS FLOAT 'Integral part of PID
DIM pid_diff AS FLOAT 'Differential part of PID
DIM pid_prev_dError[AOUTNO] AS FLOAT


'Declare other variables
DIM processIdx AS LONG
DIM eventIdx AS LONG
DIM pidIdx AS LONG
DIM nextPidTime AS LONG
DIM nextAOutTime AS LONG
DIM timer AS LONG 'timing the event duration
DIM total_workload AS LONG 'calcutaing the workload during the shot
DIM i AS LONG 'for loop index

'Declare arrays for storing AIN and setting AOUT channels
DIM set_target[AOUTNO] AS LONG  ' Set values to be written to AOUTs
DIM set_output[AOUTNO] AS LONG  ' Set values to be written to AOUTs
DIM set_pid[AOUTNO] AS LONG    ' PID selection for each AOUT
DIM act_values[PIDNO] AS LONG   ' Analog values measured from AINs


'=========================================================================
'=                                INIT                                   =
'=========================================================================
init:
  'Set Processdelay to 2us
  PROCESSDELAY = 2000
  par_1 = 1 'Process Status
  par_4 = 0 'Wait counter
  par_6 = 0 'Retrigger wait

  'Initialize Variables
  processIdx = 0
  eventIdx = 0
  pidIdx = 0
  total_workload = 0
  nextPidTime = DATA_4[1]
  nextAOutTime = DATA_1[1]

  '=========================== INITIALIZE TICOS ========================== 
  'Set DIO channels as outputs
  P2_DigProg(DIO1, 1111b)     'Channel 0-31 as outputs
  P2_DigProg(DIO2, 1111b)     'Channel 32-63 as outputs

  'Initialize pointers to Tico memory
  P2_TiCo_Reset(000011b)
  P2_TDrv_Init(DIO1, 1, PTR_TICO1)    'Data Transfer to Module DIO1
  P2_TDrv_Init(DIO2, 1, PTR_TICO2)    'Data Transfer Module DIO2

  'Load digital event data to tico 1
  P2_SetData_Long(PTR_TICO1, 1, 1, MAX_TICO_EVENTS, DATA_10, 1, 1) 'DIO1 TiCo times
  P2_SetData_Long(PTR_TICO1, 2, 1, MAX_TICO_EVENTS, DATA_11, 1, 1) 'DIO1 digital output values

  'Load digital event data to tico 2
  P2_SetData_Long(PTR_TICO2, 1, 1, MAX_TICO_EVENTS, DATA_20, 1, 1) 'DIO2 TiCo times
  P2_SetData_Long(PTR_TICO2, 2, 1, MAX_TICO_EVENTS, DATA_21, 1, 1) 'DIO2 digital output values

  'Initialize Digital Channels
  P2_Set_Par(DIO1,1,1,DATA_11[1])   'DIO1 digital output values
  P2_Set_Par(DIO2,1,1,DATA_21[1])   'DIO2 digital output values

  'Initialize time counter for tico to synchronize to analog channels
  P2_Set_Par(DIO1,1,2,81)
  P2_Set_Par(DIO2,1,2,81)

  'Initialize event counter for digital channels
  P2_Set_Par(DIO1,1,3,2)
  P2_Set_Par(DIO2,1,3,2)
  
  'Set wait start of TiCo (must pause at same time as main process)
  P2_Set_Par(DIO1,1,4,Par_9)
  P2_Set_Par(DIO2,1,4,Par_19)
  
  '===========================  PID SETTINGS  ============================
  'Initialize Integrator and Difference
  FOR i=1 TO AOUTNO
    pid_sum[i]=0
    pid_prev_dError[i]=0
  NEXT i

  '=========================== INITIALIZE AOUTS ==========================
  ' Initialize set values of all output channels
  FOR i=1 TO AOUTNO
    set_target[i]=ZERO
    set_pid[i]=0 'At beginning all PIDs off
  NEXT i
  ' Set outputs to values at t=0, if given
  FOR i=1 TO AOUTNO
    IF (DATA_1[i]=0) THEN
      set_target[DATA_2[i]] = DATA_3[i]    
    ENDIF
  NEXT i
  
  'Write analog out values
  P2_Write_DAC8(AOUT1,set_target,1)
  P2_Write_DAC8(AOUT2,set_target,9)
  'Output set voltages
  P2_Start_DAC(AOUT1)
  P2_Start_DAC(AOUT2)
  
  '=========================== INITIALIZE PIDs  ==========================
  FOR i=1 TO par_22
    pidn = DATA_24[i]
    pid_P[pidn] = DATA_25[i]
    pid_I[pidn] = DATA_26[i]
    pid_D[pidn] = DATA_27[i]
    pid_min[pidn] = DATA_28[i]
    pid_max[pidn] = DATA_29[i]
  NEXT i
  

  '===========================  OTHER SETTINGS  ==========================

  'Turn LEDs ON
  P2_Set_Led(DIO1, 1)
  P2_Set_Led(DIO2, 1)
  P2_Set_Led(AIN1, 1)
  P2_Set_Led(AIN2, 1)
  P2_Set_Led(AOUT1, 1)
  P2_Set_Led(AOUT2, 1)

  '========================== AIN CONFIGURATION ==========================
  'Set P2_ADCF_Mode - leave it set standard (=0) here since later the sampling rate is set by hand
  P2_ADCF_Mode(2^(AIN1-1),0)
  'Average over 4 sample values
  P2_Set_Average_Filter(AIN1,2)
  'Set P2_ADCF_Mode - leave it set standard (=0) here since later the sampling rate is set by hand
  P2_ADCF_Mode(2^(AIN2-1),0)
  'Average over 4 sample values
  P2_Set_Average_Filter(AIN2,2)

  'Set Gain of AIN Channels
  FOR i=1 TO 8
    P2_Set_Gain(AIN1,i,DATA_9[i])
    P2_Set_Gain(AIN2,i,DATA_9[i+8])
  NEXT i
  
  'Determine indices for analog data acquisition
  ain_index[1] = 1
  FOR i=2 TO AINNO
    ain_index[i] = ain_index[i-1] + DATA_8[i-1] - DATA_7[i-1]
  NEXT i


  '### Set the Sampling Rate of the AIN cards. The Period is given by T = 250ns + (value-1)* 10ns. The value is set by writing to the correct register using POKE(register,value)
  CHECK_CARD(AIN1)
  POKE((68050100h OR  shift_left(AIN1,20)),1)

  CHECK_CARD(AIN2)
  POKE((68050100h OR  shift_left(AIN2,20)),1)

  'Start Conversion for first event
  P2_Sync_All(001100b)
  'Wait for 200 * 10ns to make sure that first ADC values are ready
  CPU_Sleep(200) ' TODO: Do we still need to wait if we set DIOs after Sync All?

  'Set I/O of T12
  ' DIG I/O-0 as input with rising edge
  ' DIG I/O-1 as output
  CPU_Dig_IO_Config(110010b)
  CPU_Digout(1,1)

  ' Set first output values at DIOs
  P2_DIGOUT_LONG(DIO1,DATA_11[1])
  P2_DIGOUT_LONG(DIO2,DATA_21[1])


  '=========================================================================
  '=                               EVENT LOOP                              =
  '=========================================================================

EVENT:
  timer = Read_Timer_Sync()

  '======================== READ ANALOG IN CARDS =========================

  'Read act_values at all ADC Channels
  P2_READ_ADCF8(AIN1, act_values, 1)    'READ CHANNEL 1-8 OF AIN MODULE 1
  P2_READ_ADCF8(AIN2, act_values, 9)   'READ CHANNEL 1-8 OF AIN MODULE 2

  'Start conversion at all ADC Channels Synced for next Event
  P2_Sync_All(001100b)
  
  'Synchronize DIO Channels (once after 20 events)
  if(processIdx = 20) then
    P2_set_par(DIO1,1,20,1)    'start tico event
    P2_set_par(DIO2,1,20,1)    'start tico event
  endif
  
  'Set all voltages synchronously
  P2_Sync_All(110000b)

  '======================= INCREASE TIME (IF NO WAIT) ======================
  '======================= SAVE MEASURED AIN VALUES ======================
  IF (Par_3 <> processIdx) THEN
    inc processIdx
    ' Write ADC Values
    ' When there is a wait, do not save data
    FOR i=1 to AINNO
      IF(processIdx <= DATA_8[i]) THEN
        IF (processIdx > DATA_7[i]) THEN
          DATA_199[ain_index[i]]=act_values[i]
          inc ain_index[i]
        ENDIF 'processIdx > DATA_7[i]
      ENDIF 'processIdx <= DATA_8[i]
    NEXT i
  ELSE
    ' If Par_3 == processIdx we reached a wait. This means we pause the 'clock' until we get the singnal to continue.
    ' This signal can either be that Par_6 was set to 1, or we reach the timeout (in Par_5)
    IF ((Par_6 = 1) OR (Par_4 = Par_5)) THEN
      Par_3 = -1 'Disable wait
      ' Resume TiCo processes. Before we do that, we reduce the time counter of the TiCos.
      ' This is necessary because otherwise the outputs are not in sync with before the wait anymore.
      ' I don't understand why the offset is a full 500ns more for DIO1 (just from the P2_Set_Par order below?), 
      ' but this was necessary from the oscillorsope measurements.
      P2_Set_Par(DIO1,1,2,P2_Get_Par(DIO1,1,2)-5)
      P2_Set_Par(DIO2,1,2,P2_Get_Par(DIO2,1,2)-4)
      P2_Set_Par(DIO1,1,4,-1) 'Resume DIO1
      P2_Set_Par(DIO2,1,4,-1) 'Resume DIO2
    ENDIF
    inc Par_4
  ENDIF
  

  '=========================== CHECK END OF RUN ==========================
  IF (processIdx >= par_2) THEN
    END 'end loop when last last timing event completed
  ENDIF

  '========================= Update target values ========================
  IF(nextAOutTime <= processIdx) THEN
    DO
      inc eventIdx
      set_target[DATA_2[eventIdx]]=DATA_3[eventIDX]
    UNTIL(DATA_1[eventIdx+1] > processIdx)
    nextAOutTime = DATA_1[eventIdx+1]
  ENDIF
  
    
  '====================== CALCULATE NEW SET VALUES (PIDs) =======================

  FOR i=1 TO AOUTNO
    pidn = set_pid[i]
    if (pidn = 0) then
      'No PID active
      set_output[i]=set_target[i]
    else
      'Get deviation from target voltage
      pid_error = set_target[i]- act_values[pidn]
      'Get proportional part
      pid_lin=pid_P[pidn]*pid_error
      'Get integral part
      pid_sum[i] = pid_sum[i] + pid_I[pidn]*pid_error
      'Get differential part
      pid_dError = pid_D[pidn]* pid_error
      pid_diff = pid_dError - pid_prev_dError[i]
      pid_prev_dError[i] = pid_dError

      'Check for integral overflow
      if (pid_sum[i] > N) then pid_sum[i] = N
      if (pid_sum[i] < -N) then pid_sum[i] = -N

      set_output[i]=(pid_lin+pid_sum[i]+pid_diff) + N
      ' Check that output is within safe limits
      if (set_output[i] < pid_min[pidn]) then set_output[i] = pid_min[pidn]
      if (set_output[i] > pid_max[pidn]) then set_output[i] = pid_max[pidn]
    endif
  NEXT i

  '========================== Update pid target ==========================
  IF(nextPidTime <= processIdx) Then
    DO
      inc pidIdx
      i = DATA_5[pidIdx] ' output channel index
      set_pid[i] = DATA_6[pidIdx] ' input/PID channel index
      pid_prev_dError[i] = 0
      

      IF (set_pid[i]=0) THEN
        ' When we turn off PID, use the last output value as the new target value.
        ' With this we can turn a beam off and on with the previous power during one shot.
        IF (DATA_30[pidIdx]=100000) THEN set_target[i] = set_output[i]
      ELSE
        ' Set output value when PID is tunred on. Because we don't have an input value yet, use just the I part.
        ' (Either the I value from the previous PID time, or the one set in Data_30.
        IF (DATA_30[pidIdx] = 100000) THEN
          set_output[i] = pid_sum[i] + N
        ELSE
          set_output[i] = DATA_30[pidIdx]
          pid_sum[i] = set_output[i] - N
        ENDIF
      ENDIF
      
    UNTIL(DATA_4[pidIdx+1] > processIdx)
    nextPidTime = DATA_4[pidIdx+1]
  ENDIF
  
  '========================= SET AOUT VALUES =========================
  'Write values to AOUT Cards
  P2_Write_DAC8(AOUT1,set_output,1)
  P2_Write_DAC8(AOUT2,set_output,9)

  '### Debug Timer
  timer=READ_TIMER_SYNC() - timer

  ' CAN BE REMOVED IN REAL USAGE
  IF (processIdx<MAX_EVENTS) THEN
    DATA_31[processIdx] = timer
  ENDIF

  total_workload = total_workload + timer

  par_15=processIdx

FINISH:
  CPU_Digout(1,0)

  'Turn Module LEDs OFF
  P2_Set_Led(DIO1,0)
  P2_Set_Led(DIO2,0)
  P2_Set_Led(AIN1,0)
  P2_Set_Led(AIN2,0)
  P2_Set_Led(AOUT1,0)
  P2_Set_Led(AOUT2,0)

  ' Check if TiCo Status was fine
  par_10 = P2_Process_Status(DIO1,1,1)
  par_20 = P2_Process_Status(DIO2,1,1)
  'Stop Tico Processes
  P2_TiCo_Stop_Process(PTR_TICO1,1)
  P2_TiCo_Stop_Process(PTR_TICO2,1)

  'Set values of all output channels to 0V
  'for i=1 to AOUTNO
  '  set_output[i]=ZERO
  'next i

  'Write analog out values
  P2_Write_DAC8(AOUT1,set_output,1)
  P2_Write_DAC8(AOUT2,set_output,9)
  'Output set voltages
  P2_Start_DAC(AOUT1)
  P2_Start_DAC(AOUT2)

  PAR_13 = total_workload
  PAR_1 = 0
