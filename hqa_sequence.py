from labscript import *
# from labscript import DigitalOut, AnalogIn
from user_devices.ADwinProII.labscript_devices_ADwin_modules import *
from user_devices.ADwinProII.labscript_devices import ADwinProII
from user_devices.ADwinProII.labscript_devices_ADwin_modules import ADwinAI8,ADwinAO8,ADwinDIO32
from user_devices.DDS_AS065.labscript_devices import DDS_AS065

import routines.experiment_blocks as experiment

from user_devices import unitconversions

# Create ADwin-Pro II Hardware
ADwinProII("ADwin", 1, process_buffered, process_manual, mock=True)
ADwinDIO32("DIO32_1", ADwin, module_address=1, TiCo=True)
ADwinDIO32("DIO32_2", ADwin, module_address=2, TiCo=True)
ADwinAO8("AO8_1", ADwin, module_address=5)
ADwinAO8("AO8_2", ADwin, module_address=6)
ADwinAI8("AI8_1", ADwin, module_address=3)
ADwinAI8("AI8_2", ADwin, module_address=4)

DDS_AS065("DDS1", parent_device=DIO32_1, connection="13", device_address="10.14.1.8", device_port=80, mock=True)

# Digital Outputs
# DigitalOut("Shutter_Cooler", parent_device=DIO32_1, connection="1")
Shutter("Shutter_Cooler", parent_device=DIO32_1, connection="1", delay=(0, 0), open_state=0)
# DigitalOut("Shutter_Repump", parent_device=DIO32_1, connection="2")
Shutter("Shutter_Repump", parent_device=DIO32_1, connection="2", delay=(0, 0), open_state=0)
# DigitalOut("Shutter_2D_MOT", parent_device=DIO32_1, connection="3")
Shutter("Shutter_2D_MOT", parent_device=DIO32_1, connection="3", delay=(0, 0), open_state=0)
# DigitalOut("Shutter_Push_Beam", parent_device=DIO32_1, connection="4")
Shutter("Shutter_Push_Beam", parent_device=DIO32_1, connection="4", delay=(0, 0), open_state=0)
# DigitalOut("Shutter_MOT3", parent_device=DIO32_1, connection="5")
Shutter("Shutter_MOT3", parent_device=DIO32_1, connection="5", delay=(0, 0), open_state=1)
# DigitalOut("", parent_device=DIO32_1, connection="6")
# DigitalOut("", parent_device=DIO32_1, connection="7")
# DigitalOut("", parent_device=DIO32_1, connection="8")
DigitalOut("Switch_Coil_R2", parent_device=DIO32_1, connection="9")
DigitalOut("Switch_Coil_L1", parent_device=DIO32_1, connection="10")
DigitalOut("Switch_Coil_R1_plus_L2", parent_device=DIO32_1, connection="11")
DigitalOut("DOUT_Channel12", parent_device=DIO32_1, connection="12")
# DigitalOut("", parent_device=DIO32_1, connection="13")
# DigitalOut("", parent_device=DIO32_1, connection="14")
# DigitalOut("", parent_device=DIO32_1, connection="15")
# DigitalOut("", parent_device=DIO32_1, connection="16")
# DigitalOut("Shutter_Accordion", parent_device=DIO32_1, connection="17")
Shutter("Shutter_Accordion", parent_device=DIO32_1, connection="17", delay=(0, 0), open_state=0)
# DigitalOut("Shutter_DMD", parent_device=DIO32_1, connection="18")
Shutter("Shutter_DMD", parent_device=DIO32_1, connection="18", delay=(0, 0), open_state=0)
# DigitalOut("Shutter_808", parent_device=DIO32_1, connection="19")
Shutter("Shutter_808", parent_device=DIO32_1, connection="19", delay=(0, 0), open_state=1)
# DigitalOut("Shutter_Tweezer", parent_device=DIO32_1, connection="20")
Shutter("Shutter_Tweezer", parent_device=DIO32_1, connection="20", delay=(0, 0), open_state=0)
Trigger("Trigger_Camera", parent_device=DIO32_1, connection="21")
# DigitalOut("Shutter_HODT", parent_device=DIO32_1, connection="22")
Shutter("Shutter_HODT", parent_device=DIO32_1, connection="22", delay=(0, 0), open_state=0)
# DigitalOut("Shutter_VODT", parent_device=DIO32_1, connection="23")
Shutter("Shutter_VODT", parent_device=DIO32_1, connection="23", delay=(0, 0), open_state=0)
# DigitalOut("Shutter_eHODT", parent_device=DIO32_1, connection="24")
Shutter("Shutter_eHODT", parent_device=DIO32_1, connection="24", delay=(0, 0), open_state=0)
# DigitalOut("Trigger_MOT_Logging", parent_device=DIO32_1, connection="25")
Trigger("Trigger_MOT_Logging", parent_device=DIO32_1, connection="25")
DigitalOut("Trigger_Orca_Quest", parent_device=DIO32_1, connection="26")
DigitalOut("RF_Switch", parent_device=DIO32_1, connection="27")
DigitalOut("RF_DDS_Trigger", parent_device=DIO32_1, connection="28")
DigitalOut("Trigger_Monitoring", parent_device=DIO32_1, connection="29")
DigitalOut("Trigger_Tweezer_Modulation", parent_device=DIO32_1, connection="30")
DigitalOut("Trigger_VODT_Modulation", parent_device=DIO32_1, connection="31")
DigitalOut("Trigger_HODT_PD_Logging", parent_device=DIO32_1, connection="32")

DigitalOut("Switch_Imaging1_AOM", parent_device=DIO32_2, connection="1")
# DigitalOut("Shutter_Imaging1", parent_device=DIO32_2, connection="2")
Shutter("Shutter_Imaging1", parent_device=DIO32_2, connection="2", delay=(0, 0), open_state=0)
# DigitalOut("Shutter_Imaging2", parent_device=DIO32_2, connection="3")
Shutter("Shutter_Imaging2", parent_device=DIO32_2, connection="3", delay=(0, 0), open_state=0)
DigitalOut("Switch_Imaging2_AOM", parent_device=DIO32_2, connection="4")
# DigitalOut("Shutter_Absorption", parent_device=DIO32_2, connection="5")
Shutter("Shutter_Absorption", parent_device=DIO32_2, connection="5", delay=(0, 0), open_state=0)
# DigitalOut("", parent_device=DIO32_2, connection="6")
# DigitalOut("", parent_device=DIO32_2, connection="7")
# DigitalOut("", parent_device=DIO32_2, connection="8")
# DigitalOut("", parent_device=DIO32_2, connection="9")
# DigitalOut("", parent_device=DIO32_2, connection="10")
# DigitalOut("", parent_device=DIO32_2, connection="11")
# DigitalOut("", parent_device=DIO32_2, connection="12")
# DigitalOut("", parent_device=DIO32_2, connection="13")
# DigitalOut("", parent_device=DIO32_2, connection="14")
# DigitalOut("", parent_device=DIO32_2, connection="15")
# DigitalOut("", parent_device=DIO32_2, connection="16")
# DigitalOut("", parent_device=DIO32_2, connection="17")
# DigitalOut("", parent_device=DIO32_2, connection="18")
# DigitalOut("", parent_device=DIO32_2, connection="19")
# DigitalOut("", parent_device=DIO32_2, connection="20")
# DigitalOut("", parent_device=DIO32_2, connection="21")
# DigitalOut("", parent_device=DIO32_2, connection="22")
# DigitalOut("", parent_device=DIO32_2, connection="23")
# DigitalOut("", parent_device=DIO32_2, connection="24")
# DigitalOut("", parent_device=DIO32_2, connection="25")
# DigitalOut("", parent_device=DIO32_2, connection="26")
# DigitalOut("", parent_device=DIO32_2, connection="27")
# DigitalOut("", parent_device=DIO32_2, connection="28")
# DigitalOut("", parent_device=DIO32_2, connection="29")
DigitalOut("Trigger_Rigol_Microwave", parent_device=DIO32_2, connection="30")
# DigitalOut("Shutter_Nuvu", parent_device=DIO32_2, connection="31")
Shutter("Shutter_Nuvu", parent_device=DIO32_2, connection="31", delay=(0, 0), open_state=0)
DigitalOut("Switch_Microwave", parent_device=DIO32_2, connection="32")

# Analog Outputs
ADwinAnalogOut("VCO_Repump", parent_device=AO8_1, connection="1")
ADwinAnalogOut("Mixer_Cooler", parent_device=AO8_1, connection="2")
ADwinAnalogOut("Mixer_Repump", parent_device=AO8_1, connection="3")
ADwinAnalogOut("VCO_Cooler", parent_device=AO8_1, connection="4")
ADwinAnalogOut("Mixer_eHODT", parent_device=AO8_1, connection="5")
ADwinAnalogOut("Mixer_808_Shielding", parent_device=AO8_1, connection="6")
ADwinAnalogOut("AOUT_7", parent_device=AO8_1, connection="7")
ADwinAnalogOut("Mixer_808_Tweezer", parent_device=AO8_1, connection="8")

ADwinAnalogOut("Coil_R1_plus_L2", parent_device=AO8_2, connection="1", unit_conversion_class=unitconversions.OffsetField)
ADwinAnalogOut("Coil_L1", parent_device=AO8_2, connection="2")
ADwinAnalogOut("Coil_R2", parent_device=AO8_2, connection="3")
ADwinAnalogOut("Mixer_HODT", parent_device=AO8_2, connection="4")
ADwinAnalogOut("Mixer_VODT", parent_device=AO8_2, connection="5")
ADwinAnalogOut("Mixer_Tweezer", parent_device=AO8_2, connection="6")
ADwinAnalogOut("Mixer_Accordion", parent_device=AO8_2, connection="7")
ADwinAnalogOut("AOUT_16", parent_device=AO8_2, connection="8")

# Analog Inputs
AnalogIn("Photodiode_MOT2", parent_device=AI8_1, connection="1")
AnalogIn("Photodiode_VODT", parent_device=AI8_1, connection="2")
AnalogIn("Photodiode_Tweezer_Gain1", parent_device=AI8_1, connection="3")
AnalogIn("Photodiode_HODT", parent_device=AI8_1, connection="4")
AnalogIn("Photodiode_Tweezer_Gain50", parent_device=AI8_1, connection="5")
AnalogIn("LEM_Coil_R2", parent_device=AI8_1, connection="6")
AnalogIn("LEM_Coil_L1", parent_device=AI8_1, connection="7")
AnalogIn("LEM_Coil_R1_plus_L2", parent_device=AI8_1, connection="8")

AnalogIn("Photodiode_MOT1_Gain1", parent_device=AI8_2, connection="1")
AnalogIn("Photodiode_MOT3", parent_device=AI8_2, connection="2")
AnalogIn("Photodiode_eHODT", parent_device=AI8_2, connection="3")
AnalogIn("Photodiode_Shielding", parent_device=AI8_2, connection="4")
AnalogIn("AIN_13", parent_device=AI8_2, connection="5")
AnalogIn("Photodiode_808_Tweezer_Gain1", parent_device=AI8_2, connection="6")
AnalogIn("Photodiode_808_Tweezer_Gain50", parent_device=AI8_2, connection="7")
AnalogIn("AIN_16", parent_device=AI8_2, connection="8")



if __name__ == '__main__':
    # devices = devices.Devices()
    # hqa = experiment.Experiment(devices)

    start() 

    t = 0 * us

    add_time_marker(t, "Initialize Experiment")
    t = experiment.initialize(t)

    add_time_marker(t, "Start MOT Loading")
    t = experiment.mot_loading(t)

    add_time_marker(t, "Start MOT Compression")
    t = experiment.mot_compression(t)

    add_time_marker(t, "Start MOT Release")
    t = experiment.release_recapture(t)

    if use_hodt or use_vodt or use_tweezer:
        add_time_marker(t, "Start ODT")
        experiment.odt_prep(t)
        if use_hodt:
            t_hodt = experiment.hodt(t)
        if use_vodt:
            t_vodt = experiment.vodt(t)
        if use_tweezer:
            t_tweezer = experiment.tweezer(t)

    t = max(t_hodt, t_vodt, t_tweezer)

    add_time_marker(t, "Spilling")
    t = experiment.spilling(t)



    add_time_marker(t, "Start MOT Recapture")
    t = experiment.release_recapture_2(t)

    add_time_marker(t, "Start MOT Image")
    t = experiment.odt_imaging(t)

    add_time_marker(t, "Reset")
    t = experiment.reset(t)

    stop(t + 100 * us)
