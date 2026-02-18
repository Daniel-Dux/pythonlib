from labscript import *

def initialize(t):
    
    initialize_time = 100*ms
    
    ####################
    # Digital Outputs
    ####################
    
    # Shutters
    Shutter_Cooler.go_high(t)
    Shutter_Absorption.go_low(t)
    Shutter_808.go_low(t)
    Shutter_DMD.go_high(t)
    Shutter_Accordion.go_high(t)
    Shutter_MOT3.go_low(t)
    Shutter_Nuvu.go_high(t)
    
    # AOMs
    Switch_Imaging1_AOM.go_high(t)
    Switch_Imaging2_AOM.go_high(t)
    
    # Magnetic Field Switches
    Switch_Coil_R2.go_high(t)
    Switch_Coil_L1.go_high(t)
    Switch_Coil_R1_plus_L2.go_high(t)
    
    DOUT_Channel12.go_high(t)
    
    ###################
    # Analog Outputs
    ###################
    
    # =========================================================================
    # Initialize PID parameters (once at start of shot)
    # =========================================================================
    
    # Magnetic Coils - use LEM current sensors as feedback
    Coil_R1_plus_L2.init_PID(LEM_Coil_R1_plus_L2, P=pid_coil23_p, I=pid_coil23_i, D=pid_coil23_d)
    Coil_L1.init_PID(LEM_Coil_L1, P=pid_coil1_p, I=pid_coil1_i, D=pid_coil1_d)
    Coil_R2.init_PID(LEM_Coil_R2, P=pid_coil4_p, I=pid_coil4_i, D=pid_coil4_d)
    
    # Optical Dipole Traps - use photodiodes as feedback
    Mixer_HODT.init_PID(Photodiode_HODT, P=pid_hodt_p, I=pid_hodt_i, D=pid_hodt_d)
    Mixer_VODT.init_PID(Photodiode_VODT, P=pid_vodt_p, I=pid_vodt_i, D=pid_vodt_d)
    Mixer_eHODT.init_PID(Photodiode_eHODT, P=pid_ehodt_p, I=pid_ehodt_i, D=pid_ehodt_d)
    
    # Tweezer - two different gain photodiodes for different power ranges
    Mixer_Tweezer.init_PID(Photodiode_Tweezer_Gain50, P=pid_tweezer_p, I=pid_tweezer_i, D=pid_tweezer_d)
    # Alternative: Mixer_Tweezer.init_PID(Photodiode_Tweezer_Gain1, P=pid_tweezer_low_p, I=pid_tweezer_low_i, D=pid_tweezer_low_d)
    
    # 808nm Tweezer
    Mixer_808_Tweezer.init_PID(Photodiode_808_Tweezer_Gain50, P=pid_808_p, I=pid_808_i, D=pid_808_d)
    
    # =========================================================================
    # Activate PIDs at time t=0
    # =========================================================================
    
    # Activate Coil PIDs
    Coil_R1_plus_L2.set_PID(t, LEM_Coil_R1_plus_L2, set_output=0)
    Coil_L1.set_PID(t, LEM_Coil_L1, set_output=0)
    Coil_R2.set_PID(t, LEM_Coil_R2, set_output=0)
    
    # Analog Channels
    VCO_Repump.constant(t, vco_repump)
    Mixer_Repump.constant(t, power_repump_load)
    VCO_Cooler.constant(t, vco_cooler)
    Mixer_Cooler.constant(t, 0.39)
    Mixer_808_Tweezer.constant(t, 1)
    Coil_R1_plus_L2.constant(t, 0)
    Coil_L1.ramp(t, initialize_time, 0, imag_mot_coil1, adwin_ramp_sampling_rate)
    Coil_R2.ramp(t, initialize_time, 0, imag_mot_coil4, adwin_ramp_sampling_rate)
    Mixer_HODT.constant(t, hodt_power_heating)
    
    t += initialize_time
    
    return t

def mot_loading(t):
    VCO_Repump.constant(t, vco_repump)
    VCO_Cooler.constant(t, vco_cooler)
    Mixer_Cooler.constant(t, power_cooler_load)
    Mixer_Repump.constant(t, power_repump_load)
    Coil_L1.constant(t, imag_mot_coil1)
    Coil_R2.constant(t, imag_mot_coil4)
    
    Trigger_MOT_Logging.trigger(t+10*ms, trigger_duration)
    
    t += mot_loading_duration
    
    Shutter_Push_Beam.close(t)
    Shutter_2D_MOT.close(t)
    
    return t

def release_recapture(t):
    Shutter_2D_MOT.close(t)
    
    Mixer_Cooler.constant(t, 0)
    Mixer_Repump.constant(t, 0)
    
    Coil_L1.constant(t, 0)
    Coil_R2.constant(t, 0)
    
    return t

def mot_compression(t):
    VCO_Repump.ramp(t+comp_freq_start, comp_freq_duration, comp_repump_freq_start, comp_repump_freq_end, adwin_ramp_sampling_rate)
    VCO_Cooler.ramp(t+comp_freq_start, comp_freq_duration, comp_cooler_freq_start, comp_cooler_freq_end, adwin_ramp_sampling_rate)
    Mixer_Repump.ramp(t+comp_power_start, comp_power_duration, comp_repump_power_start, comp_repump_power_end, adwin_ramp_sampling_rate)
    Mixer_Cooler.ramp(t+comp_power_start, comp_power_duration, comp_cooler_power_start, comp_cooler_power_end, adwin_ramp_sampling_rate)
    
    Coil_R1_plus_L2.ramp(t+comp_coil_start, comp_coil_duration, comp_coil23_start, comp_coil23_end, adwin_ramp_sampling_rate, units='G')
    Coil_L1.ramp(t+comp_coil_start, comp_coil_duration, comp_coil1_start, comp_coil1_end, adwin_ramp_sampling_rate)
    Coil_R2.ramp(t+comp_coil_start, comp_coil_duration, comp_coil4_start, comp_coil4_end, adwin_ramp_sampling_rate)
    
    t += np.max([comp_freq_start+comp_freq_duration, comp_power_start+comp_power_duration, comp_coil_start+comp_coil_duration])
    
    return t

def release_recapture_2(t):
    """
    Release_Recapture_2 block - prepares atoms for ODT transfer
    """
    
    # ===================
    # Digital Events
    # ===================
    
    Switch_Coil_R2.go_low(t + recapture_coil_switch - 5*ms)
    Switch_Coil_R2.go_high(t + recapture_coil_switch + 5*ms)
    
    Switch_Coil_L1.go_low(t + recapture_coil_switch - 5*ms)
    Switch_Coil_L1.go_high(t + recapture_coil_switch + 5*ms)
    
    Switch_Coil_R1_plus_L2.go_low(t + recapture_coil_switch)
    DOUT_Channel12.go_low(t + recapture_coil_switch)
    
    Shutter_Cooler.go_low(t - 2*ms)
    Shutter_Repump.go_low(t - 7*ms)
    Shutter_808.go_low(t + 7*ms)
    Shutter_HODT.go_low(t + 7*ms)
    Shutter_VODT.go_low(t + 7*ms)
    
    # ===================
    # Analog Events
    # ===================
    
    VCO_Repump.constant(t + recapture_release_time, vco_repump)
    VCO_Repump.ramp(t + recapture_hold + recapture_release_time, 
                    recapture_recomp_time, 
                    vco_repump, 
                    imag_odt_vco_repump, 
                    adwin_ramp_sampling_rate)
    
    Mixer_Cooler.constant(t + recapture_release_time - aom_on_delay, 0)
    Mixer_Cooler.constant(t + recapture_release_time, power_cooler_load)
    Mixer_Cooler.ramp(t + recapture_hold + recapture_release_time,
                      recapture_recomp_time,
                      power_cooler_load,
                      imag_odt_power_cooler,
                      adwin_ramp_sampling_rate)
    
    Mixer_Repump.constant(t + recapture_release_time - aom_on_delay, 0)
    Mixer_Repump.constant(t + recapture_release_time, power_repump_load)
    Mixer_Repump.ramp(t + recapture_hold + recapture_release_time,
                      recapture_recomp_time,
                      power_repump_load,
                      imag_odt_power_repump,
                      adwin_ramp_sampling_rate)
    
    VCO_Cooler.constant(t + recapture_release_time, vco_cooler)
    VCO_Cooler.ramp(t + recapture_hold + recapture_release_time,
                    recapture_recomp_time,
                    vco_cooler,
                    imag_odt_vco_cooler,
                    adwin_ramp_sampling_rate)
    
    Coil_R1_plus_L2.constant(t + recapture_release_time, 0)
    
    Coil_L1.ramp(t + recapture_release_coil, 0.1*ms, 0, recapture_coil1_load, adwin_ramp_sampling_rate)
    Coil_L1.ramp(t + recapture_hold + recapture_release_coil,
                 recapture_recomp_time,
                 recapture_coil1_load,
                 recapture_coil1_imag,
                 adwin_ramp_sampling_rate)
    
    Coil_R2.ramp(t + recapture_release_coil, 0.1*ms, 0, recapture_coil4_load, adwin_ramp_sampling_rate)
    Coil_R2.ramp(t + recapture_hold + recapture_release_coil,
                 recapture_recomp_time,
                 recapture_coil4_load,
                 recapture_coil4_imag,
                 adwin_ramp_sampling_rate)
    
    Mixer_808_Tweezer.constant(t, 0)
    Mixer_HODT.constant(t, 0)
    Mixer_VODT.constant(t, 0)
    Mixer_Tweezer.constant(t, 0)
    
    # Calculate end time: latest action is at (recapture_hold + recapture_release_time/coil + recapture_recomp_time)
    t += recapture_hold + max(recapture_release_time, recapture_release_coil) + recapture_recomp_time
    
    return t

# =============================================================================
# Block 6: MOT Imaging (Block Active = FALSE)
# =============================================================================
def mot_imaging(t):
    """MOT Imaging sequence"""
    
    Trigger_Camera.trigger(t + imag_mot_start, 30*ms)
    
    Switch_Absorption_AOM.go_high(t - 10*ms)
    
    VCO_Repump.constant(t + imag_mot_freq_rep_start, imag_mot_vco_repump)
    Mixer_Cooler.ramp(t + imag_mot_power_cool_start, 0.001*ms, 0, imag_mot_power_cooler, adwin_ramp_sampling_rate)
    Mixer_Repump.ramp(t + imag_mot_power_rep_start, 0.001*ms, 0, imag_mot_power_repump, adwin_ramp_sampling_rate)
    VCO_Cooler.constant(t + imag_mot_freq_cool_start, imag_mot_vco_cooler)
    
    Coil_R1_plus_L2.ramp(t + imag_mot_coil23_start, 0.01*ms, 0, imag_mot_coil23, adwin_ramp_sampling_rate, units='G')
    Coil_L1.ramp(t + imag_mot_coil1_start, 0.01*ms, 0, imag_mot_coil1, adwin_ramp_sampling_rate)
    Coil_R2.ramp(t + imag_mot_coil1_start, 0.01*ms, 0, imag_mot_coil4, adwin_ramp_sampling_rate)
    
    # Letzte Aktion: Trigger_Camera.go_low bei t + imag_mot_start + 30*ms
    return t + imag_mot_start + 30*ms

# =============================================================================
# Block 7: ODT Imaging (Block Active = TRUE)
# =============================================================================
def odt_imaging(t):
    """ODT Imaging sequence"""
    
    Trigger_Camera.trigger(t + imag_odt_start, 5*ms)
    
    Shutter_Cooler.go_low(t + imag_odt_shutter_cooler)
    Shutter_Repump.go_low(t + imag_odt_shutter_repump)
    Shutter_808.go_low(t - 20*ms)
    
    # VCO_Repump.ramp(t + imag_odt_freq_rep_start, 0.001*ms, vco_repump_comp, imag_odt_vco_repump, adwin_ramp_sampling_rate)
    # Mixer_Repump.ramp(t + imag_odt_power_rep_start, 0.001*ms, 0, imag_odt_power_repump, adwin_ramp_sampling_rate)
    # VCO_Cooler.ramp(t + imag_odt_freq_cool_start, 0.001*ms, vco_cooler_comp, imag_odt_vco_cooler, adwin_ramp_sampling_rate)
    # Mixer_Cooler.ramp(t + imag_odt_power_cool_start, 0.001*ms, 0, imag_odt_power_cooler, adwin_ramp_sampling_rate)
    VCO_Repump.constant(t + imag_odt_freq_rep_start, imag_odt_vco_repump)
    Mixer_Repump.constant(t + imag_odt_power_rep_start, imag_odt_power_repump)
    VCO_Cooler.constant(t + imag_odt_freq_cool_start, imag_odt_vco_cooler)
    Mixer_Cooler.constant(t + imag_odt_power_cool_start, imag_odt_power_cooler)

    # Coil_L1.ramp(t + imag_odt_coil1_start, 0.01*ms, 0, imag_odt_coil1, adwin_ramp_sampling_rate)
    # Coil_R1_plus_L2.ramp(t + imag_odt_coil23_start, 0.01*ms, 0, imag_odt_coil23, adwin_ramp_sampling_rate)
    # Coil_R2.ramp(t + imag_odt_coil4_start, 0.01*ms, 0, imag_odt_coil4, adwin_ramp_sampling_rate)
    Coil_L1.constant(t + imag_odt_coil1_start, imag_odt_coil1)
    Coil_R1_plus_L2.constant(t + imag_odt_coil23_start, imag_odt_coil23, units='G')
    Coil_R2.constant(t + imag_odt_coil4_start, imag_odt_coil4)
    
    Coil_L1.constant(t + imag_odt_start + svodt, 0)
    Coil_R2.constant(t + imag_odt_start + svodt, 0)
    
    # Deactivate Tweezer PID before setting to zero
    Mixer_Tweezer.set_PID(t - 0.01*ms, None, set_output=0)
    Mixer_Tweezer.constant(t, 0)
    
    # Letzte Aktion: Coil_L1/R2.constant bei t + imag_odt_start + svodt
    return t + imag_odt_start + svodt

# =============================================================================
# Block 8: ODT Insitu (Block Active = FALSE)
# =============================================================================
def odt_insitu(t):
    """ODT Insitu imaging"""
    
    Trigger_Camera.trigger(t + imag_insitu_start, 1*ms)
    
    Shutter_Cooler.go_low(t - 10*ms)
    Shutter_Repump.go_low(t - 10*ms)
    Shutter_Push_Beam.go_high(t - 5.5*ms)
    
    VCO_Repump.ramp(t, 0.001*ms, vco_repump_comp, imag_insitu_vco_repump, adwin_ramp_sampling_rate)
    Mixer_Repump.constant(t, imag_insitu_power_repump)
    Mixer_Repump.constant(t + imag_insitu_flash_time, 0)
    
    VCO_Cooler.ramp(t, 0.001*ms, vco_cooler_comp, imag_insitu_vco_cooler, adwin_ramp_sampling_rate)
    Mixer_Cooler.constant(t, imag_insitu_power_cooler)
    Mixer_Cooler.constant(t + imag_insitu_flash_time, 0)
    
    # Deactivate ODT PIDs before setting to zero
    Mixer_HODT.set_PID(t - 0.02*ms, None, set_output=0)
    Mixer_VODT.set_PID(t - 0.02*ms, None, set_output=0)
    Mixer_Tweezer.set_PID(t - 0.02*ms, None, set_output=0)
    
    Mixer_HODT.constant(t - 0.01*ms, 0)
    Mixer_VODT.constant(t - 0.01*ms, 0)
    Mixer_Tweezer.constant(t - 0.01*ms, 0)
    
    Coil_L1.constant(t + 40*ms, 0)
    Coil_R2.constant(t + 40*ms, 0)
    
    # Letzte Aktion: Coil_L1/R2.constant bei t + 40*ms
    return t + 40*ms

# =============================================================================
# Block 9: Reset (Block Active = TRUE)
# =============================================================================
def reset(t):
    """Reset sequence - resets all channels to initial state"""
    
    # Close all ODT/Tweezer shutters
    Shutter_808.go_low(t - 10*ms)
    Shutter_Tweezer.go_low(t - 10*ms)
    Shutter_HODT.go_low(t - 10*ms)
    Shutter_VODT.go_low(t - 40*ms)
    Shutter_eHODT.go_low(t - 20*ms)
    
    Switch_Imaging1_AOM.go_high(t)
    Switch_Imaging2_AOM.go_low(t)
    
    Switch_Coil_R2.go_low(t)
    Switch_Coil_L1.go_low(t)
    Switch_Coil_R1_plus_L2.go_low(t)
    
    DDS1.trigger(t, 0.01*ms)
    DDS1.trigger(t + 1*ms, 0.01*ms)
    DDS1.trigger(t + 2*ms, 0.01*ms)
    DDS1.trigger(t + 3*ms, 0.01*ms)
    
    Shutter_2D_MOT.go_high(t)
    Trigger_Camera.trigger(t, 1*ms)
    
    VCO_Repump.constant(t, vco_repump)
    VCO_Cooler.constant(t, vco_cooler)
    Mixer_Cooler.constant(t, power_cooler_load)
    Mixer_Repump.constant(t, power_repump_load)
    
    # Mixer_eHODT.constant(t, ehodt_power_heating)
    Mixer_808_Shielding.constant(t, 8)
    Mixer_808_Tweezer.constant(t, 1)
    
    Coil_R1_plus_L2.constant(t, 0)
    Coil_L1.constant(t, 0)
    Coil_R2.constant(t, 0)
    
    # Deactivate all ODT/Tweezer PIDs in reset
    Mixer_HODT.set_PID(t - 0.01*ms, None, set_output=hodt_power_heating)
    Mixer_VODT.set_PID(t - 0.01*ms, None, set_output=vodt_power_heating)
    Mixer_eHODT.set_PID(t - 0.01*ms, None, set_output=0)
    Mixer_Tweezer.set_PID(t - 0.01*ms, None, set_output=tweezer_power_heating + 5)
    Mixer_808_Tweezer.set_PID(t - 0.01*ms, None, set_output=1)
    
    Mixer_HODT.constant(t, hodt_power_heating)
    Mixer_VODT.constant(t, vodt_power_heating)
    Mixer_Tweezer.constant(t, tweezer_power_heating + 5)
    
    # Letzte Aktion: DDS1.trigger bei t + 3.01*ms
    return t + 3.01*ms

# =============================================================================
# Block 10: Abs first imag (Block Active = FALSE)
# =============================================================================
def abs_first_imag(t):
    """First absorption imaging pulse"""
    
    Trigger_Camera.trigger(t + imag_1_cam, 1*ms)
    
    Switch_Absorption_AOM.go_low(t + imag_1_switch - imag_aom_delay - imag_shutter_delay)
    Shutter_Imaging1.go_high(t + imag_1_switch - imag_shutter_delay)
    Shutter_Imaging2.go_high(t + imag_1_switch - imag_shutter_delay)
    
    Switch_Imaging1_AOM.go_high(t + imag_1_switch)
    Switch_Imaging1_AOM.go_low(t + imag_1_switch + imag_1_sv)
    
    Shutter_Imaging1.go_low(t + imag_1_switch + imag_1_sv)
    Shutter_Imaging2.go_low(t + imag_1_switch + imag_1_sv)
    Switch_Absorption_AOM.go_high(t + imag_1_switch + imag_1_sv + imag_shutter_delay)
    
    # Letzte Aktion: Switch_Absorption_AOM.go_high
    return t + imag_1_switch + imag_1_sv + imag_shutter_delay

# =============================================================================
# Block 11: Abs sec. imag (Block Active = FALSE)
# =============================================================================
def abs_sec_imag(t):
    """Second absorption imaging pulse"""
    
    Trigger_Camera.trigger(t + imag_2_cam, 1*ms)
    Trigger_Camera.trigger(t + imag_3_cam, 1*ms)
    
    Shutter_Imaging1.go_high(t + imag_2_switch - imag_shutter_delay)
    Shutter_Imaging2.go_high(t + imag_2_switch - imag_shutter_delay)
    Switch_Absorption_AOM.go_low(t + imag_2_switch - imag_aom_delay - imag_shutter_delay)
    Shutter_Imaging1.go_low(t + imag_2_switch + imag_2_sv)
    Shutter_Imaging2.go_low(t + imag_2_switch + imag_2_sv)
    
    Switch_Imaging1_AOM.go_high(t + imag_2_switch)
    Switch_Imaging1_AOM.go_low(t + imag_2_switch + imag_2_sv)
    
    Switch_Absorption_AOM.go_high(t + imag_2_switch + imag_2_sv + imag_shutter_delay)
    
    Coil_L1.constant(t, 0)
    Coil_R2.constant(t, 0)
    
    # Letzte Aktion: max von Kamera-Trigger und AOM
    return t + max(imag_3_cam + 1*ms, imag_2_switch + imag_2_sv + imag_shutter_delay)

# =============================================================================
# Block 12: Flashing (Block Active = FALSE)
# =============================================================================
def flashing(t):
    """Flashing sequence for atom detection"""
    
    Switch_Imaging1_AOM.go_low(t + flash_aom_switch - 30*ms)
    DOUT_Channel47.go_high(t + flash_aom_switch - 30*ms)
    
    Trigger_Orca_Quest.trigger(t + flash_cam_trigger, flash_sv/1000)
    DOUT_Channel45.trigger(t + flash_cam_trigger, flash_sv/1000)
    
    Switch_Imaging1_AOM.go_high(t + flash_aom_switch)
    Switch_Imaging1_AOM.go_low(t + flash_aom_switch + flash_time)
    
    Switch_Imaging2_AOM.go_high(t + flash_aom_switch)
    Switch_Imaging2_AOM.go_low(t + flash_aom_switch - 30*ms)
    Switch_Imaging2_AOM.go_high(t + flash_aom_shutter + flash_time + 50*ms)
    
    DOUT_Channel47.go_low(t + flash_aom_switch)
    DOUT_Channel47.go_low(t + flash_aom_shutter + flash_time + 50*ms)
    
    DOUT_Channel46.trigger(t + flash_aom_switch, 1*ms)
    
    Shutter_Imaging1.go_high(t + flash_aom_shutter)
    Shutter_Imaging2.go_high(t + flash_aom_shutter)
    Shutter_Imaging1.go_low(t + flash_aom_shutter + flash_time + 1*ms)
    Shutter_Imaging2.go_low(t + flash_aom_shutter + flash_time + 1*ms)
    
    Switch_Imaging2_AOM.go_high(t + flash_aom_shutter)
    Switch_Imaging1_AOM.go_high(t + flash_aom_shutter + flash_time + 50*ms)
    
    Shutter_Nuvu.go_low(t - flash_orca_delay)
    Shutter_Nuvu.go_high(t - flash_orca_delay + flash_orca_delay + flash_time)
    
    Mixer_808_Tweezer.ramp(t - 100*ms, 5*ms, tw808_evap_end/50, tw808_power_dark, adwin_ramp_sampling_rate)
    
    Coil_R1_plus_L2.ramp(t - 40*ms, 10*ms, 
                         spill1_coil_field * shutoff,
                         flash_coil23 * shutoff,
                         adwin_ramp_sampling_rate, units='G')
    
    # Letzte Aktion: Switch_Imaging1_AOM.go_high bei flash_aom_shutter + flash_time + 50*ms
    return t + flash_aom_shutter + flash_time + 50*ms

# =============================================================================
# Block 13: HODT (Block Active = TRUE)
# =============================================================================
def hodt(t):
    """Horizontal Optical Dipole Trap loading and evaporation"""
    
    # Activate HODT PID
    Mixer_HODT.set_PID(t + hodt_power_start - aom_on_delay, Photodiode_HODT, set_output=0)
    
    Shutter_HODT.go_high(t + hodt_shutter_start)
    
    Mixer_HODT.constant(t + hodt_power_start - aom_on_delay, 0)
    Mixer_HODT.ramp(t + hodt_power_start, 
                    hodt_power_ramp, 
                    0, 
                    hodt_power_initial, 
                    adwin_ramp_sampling_rate)
    
    # Letzte Aktion: Mixer_HODT.ramp endet bei hodt_power_start + hodt_power_ramp
    return t + hodt_power_start + hodt_power_ramp

# =============================================================================
# Block 14: HODT Modulation (Block Active = FALSE)
# =============================================================================
def hodt_modulation(t):
    """HODT power modulation for parametric heating"""
    
    DOUT_Channel29.trigger(t + hodt_mod_trigger, 0.02*ms)
    
    # Sinusoidal modulation on Mixer_HODT
    # modulation_depth = hodt_mod_depth, period = hodt_mod_period
    # Duration: hodt_mod_time
    
    # Letzte Aktion: DOUT_Channel29 trigger
    return t + hodt_mod_trigger + 0.02*ms

# =============================================================================
# Block 15: eHODT (Block Active = FALSE)
# =============================================================================
def ehodt(t):
    """Enhanced HODT evaporation sequence"""
    
    Shutter_eHODT.go_high(t + ehodt_start)
    
    Mixer_eHODT.ramp(t + ehodt_start, 0.1*ms, 
                     ehodt_power_heating, 
                     ehodt_evap_start, 
                     adwin_ramp_sampling_rate)
    
    # Quadratic evaporation ramp
    evap_steps = 10
    for i in range(evap_steps):
        t_rel_start = i / evap_steps
        t_rel_end = (i+1) / evap_steps
        power_start = ehodt_evap_start - (ehodt_evap_start - ehodt_evap_end) * t_rel_start**2
        power_end = ehodt_evap_start - (ehodt_evap_start - ehodt_evap_end) * t_rel_end**2
        step_duration = ehodt_evap_time / evap_steps
        Mixer_eHODT.ramp(t + ehodt_evap_delay + i * step_duration, step_duration, 
                         power_start, power_end, adwin_ramp_sampling_rate)
    
    # Letzte Aktion: Evaporation ramp endet bei ehodt_evap_delay + ehodt_evap_time
    return t + ehodt_evap_delay + ehodt_evap_time

# =============================================================================
# Block 16: eHODT Modulation (Block Active = FALSE)
# =============================================================================
def ehodt_modulation(t):
    """eHODT power modulation"""
    
    # Sinusoidal modulation on Mixer_eHODT
    # modulation_depth = ehodt_mod_depth, period = ehodt_mod_period
    # Duration: ehodt_mod_time
    
    # Keine digitale/analoge Aktionen definiert - Modulation ist TODO
    return t

# =============================================================================
# Block 17: Shielding (Block Active = FALSE)
# =============================================================================
def shielding(t):
    """Shield beam for atom protection"""
    
    Shutter_808.go_high(t + shield_start)
    
    Mixer_808_Shielding.ramp(t + shield_start, shield_ramp_up,
                      8, shield_power, adwin_ramp_sampling_rate)
    
    Mixer_808_Shielding.constant(t + shield_start + shield_ramp_up, shield_power)
    
    Mixer_808_Shielding.ramp(t + shield_end, shield_ramp_down,
                      shield_power, shield_power_end, adwin_ramp_sampling_rate)
    
    Mixer_808_Shielding.constant(t + shield_end + shield_ramp_down, shield_power_end)
    
    Mixer_Tweezer.ramp(t + shield_start, 1*ms,
                       tweezer_power_heating, 
                       tweezer_power_heating + shield_tweezer_offset,
                       adwin_ramp_sampling_rate)
    
    # Letzte Aktion: Mixer_808_Shielding.constant bei shield_end + shield_ramp_down
    return t + shield_end + shield_ramp_down

# =============================================================================
# Block 18: Shielding Mod (Block Active = FALSE)
# =============================================================================
def shielding_mod(t):
    """Shield beam modulation"""
    
    DOUT_Channel30.trigger(t + shield_mod_start, 0.02*ms)
    
    # Sinusoidal modulation on Mixer_808_Shielding
    # modulation_depth = shield_mod_depth, period = shield_mod_period
    
    # Letzte Aktion: DOUT_Channel30 trigger
    return t + shield_mod_start + 0.02*ms

# =============================================================================
# Block 19: ODT Prep (Block Active = TRUE)
# =============================================================================
def odt_prep(t):
    """ODT preparation - shutting off MOT beams and ramping magnetic fields"""
    
    Shutter_Cooler.go_high(t)
    Shutter_Repump.go_high(t + 5*ms)
    
    Switch_Coil_R2.go_low(t + odt_prep_cooler_off)
    Switch_Coil_L1.go_low(t + odt_prep_cooler_off)
    
    Coil_R1_plus_L2.ramp(t + odt_prep_cooler_off, 
                         10*ms, 
                         0,
                         odt_prep_coil23_balance * shutoff, 
                         adwin_ramp_sampling_rate, units='G')
    
    Coil_L1.constant(t + odt_prep_cooler_off, 0)
    Coil_R2.constant(t + odt_prep_cooler_off, 0)
    
    Mixer_Cooler.constant(t + odt_prep_cooler_off, 0)
    Mixer_Cooler.constant(t + odt_prep_cooler_off + aom_off_delay, odt_prep_cooler_heating)
    
    Mixer_Repump.constant(t + odt_prep_repump_off, 0)
    Mixer_Repump.constant(t + odt_prep_repump_off + aom_off_delay, odt_prep_repump_heating)
    
    # Letzte Aktion: Coil_R1_plus_L2.ramp endet bei odt_prep_cooler_off + 10*ms
    return t + max(odt_prep_cooler_off + 10*ms, odt_prep_repump_off + aom_off_delay)

# =============================================================================
# Block 20: VODT (Block Active = TRUE)
# =============================================================================
def vodt(t):
    """Vertical Optical Dipole Trap loading and evaporation"""
    
    # Activate VODT PID
    Mixer_VODT.set_PID(t + vodt_power_start - aom_on_delay, Photodiode_VODT, set_output=0)
    
    Shutter_VODT.go_high(t + vodt_shutter_start)
    
    Mixer_VODT.constant(t + vodt_power_start - aom_on_delay, 0)
    
    Mixer_VODT.ramp(t + vodt_power_start,
                    vodt_power_ramp,
                    0,
                    vodt_power_initial,
                    adwin_ramp_sampling_rate)
    
    # Letzte Aktion: Mixer_VODT.ramp endet bei vodt_power_start + vodt_power_ramp
    return t + vodt_power_start + vodt_power_ramp

# =============================================================================
# Block 21: VODT Modulation (Block Active = FALSE)
# =============================================================================
def vodt_modulation(t):
    """VODT modulation for parametric excitation"""
    
    DOUT_Channel30.trigger(t + vodt_mod_delay, 0.02*ms)
    
    # Sinusoidal modulation on Mixer_VODT
    # modulation_depth = vodt_mod_depth, period = vodt_mod_period
    
    # Letzte Aktion: DOUT_Channel30 trigger
    return t + vodt_mod_delay + 0.02*ms

# =============================================================================
# Block 22: Tweezer (Block Active = TRUE)
# =============================================================================
def tweezer(t):
    """Optical tweezer loading and evaporation"""
    
    # Activate Tweezer PID
    Mixer_Tweezer.set_PID(t + tweezer_power_start - aom_on_delay, Photodiode_Tweezer_Gain50, set_output=0)
    
    Shutter_Tweezer.go_high(t + tweezer_shutter_start)
    
    Switch_Coil_R2.go_high(t + tweezer_grad_start - 20*ms)
    Switch_Coil_L1.go_high(t + tweezer_grad_start - 20*ms)
    
    Mixer_Tweezer.constant(t + tweezer_power_start - aom_on_delay, 0)
    
    Mixer_Tweezer.constant(t + tweezer_power_start, tweezer_power_initial)
    
    Mixer_Tweezer.ramp(t + tweezer_evap_plain_time,
                       tweezer_evap_ramp,
                       tweezer_power_initial,
                       tweezer_evap_end,
                       adwin_ramp_sampling_rate)
    
    # Letzte Aktion: Mixer_Tweezer evaporation ramp endet
    return t + tweezer_evap_plain_time + tweezer_evap_ramp

# =============================================================================
# Block 23: Spilling (Block Active = TRUE)
# =============================================================================
def spilling(t):
    """First spilling sequence for atom number control"""
    
    Switch_Coil_R2.go_high(t)
    Switch_Coil_L1.go_high(t)
    
    Coil_L1.ramp(t, spill_coil_ramp, 0, spill_coil_grad, adwin_ramp_sampling_rate)
    Coil_R2.ramp(t, spill_coil_ramp, 0, spill_coil_grad, adwin_ramp_sampling_rate)
    
    Coil_R1_plus_L2.ramp(t - 30*ms, spill_coil_ramp,
                         odt_prep_coil23_transfer * shutoff,
                         spill_coil_field * shutoff,
                         adwin_ramp_sampling_rate, units='G')
    
    spill_start = t + spill_coil_ramp
    Mixer_Tweezer.ramp(spill_start, spill_tweezer_ramp,
                       tweezer_evap_end, spill_tweezer_depth,
                       adwin_ramp_sampling_rate)
    
    ramp_back_start = spill_start + spill_tweezer_ramp + spill_hold
    Mixer_Tweezer.ramp(ramp_back_start, spill_tweezer_ramp,
                       spill_tweezer_depth, tweezer_evap_end,
                       adwin_ramp_sampling_rate)
    
    grad_off_start = ramp_back_start + spill_tweezer_ramp
    Coil_L1.ramp(grad_off_start, spill_coil_ramp, spill_coil_grad, 0, adwin_ramp_sampling_rate)
    Coil_R2.ramp(grad_off_start, spill_coil_ramp, spill_coil_grad, 0, adwin_ramp_sampling_rate)
    
    # Letzte Aktion: Coil ramps enden
    # grad_off_start = t + spill_coil_ramp + spill_tweezer_ramp + spill_hold + spill_tweezer_ramp
    return grad_off_start + spill_coil_ramp

# =============================================================================
# Block 24: TweezerModulation (Block Active = FALSE)
# =============================================================================
def tweezer_modulation(t):
    """Tweezer power modulation for parametric excitation"""
    
    DOUT_Channel29.trigger(t + tweezer_mod_freq_delay, 0.02*ms)
    
    Coil_R1_plus_L2.constant(t - 20*ms, tweezer_mod_coil_field * shutoff, units='G')
    Coil_L1.constant(t - 20*ms, tweezer_mod_coil_grad)
    Coil_R2.constant(t - 20*ms, tweezer_mod_coil_grad)
    
    Mixer_Tweezer.ramp(t + tweezer_mod_power_delay - 10*ms, 10*ms,
                       tweezer_evap_end,
                       tweezer_mod_power,
                       adwin_ramp_sampling_rate)
    
    Mixer_Tweezer.ramp(t + tweezer_mod_power_delay + tweezer_mod_time, 10*ms,
                       tweezer_mod_power,
                       tweezer_evap_end,
                       adwin_ramp_sampling_rate)
    
    # Letzte Aktion: Mixer_Tweezer ramp back endet
    return t + tweezer_mod_power_delay + tweezer_mod_time + 10*ms

# =============================================================================
# Block 25: Spilling 2 (Block Active = FALSE)
# =============================================================================
def spilling_2(t):
    """Second spilling sequence"""
    
    Coil_L1.ramp(t + spill2_start, spill2_coil_ramp, 0, spill2_coil_grad, adwin_ramp_sampling_rate)
    Coil_R2.ramp(t + spill2_start, spill2_coil_ramp, 0, spill2_coil_grad, adwin_ramp_sampling_rate)
    
    Coil_R1_plus_L2.ramp(t + spill2_start - 20*ms, spill2_coil_ramp,
                         spill1_coil_field * shutoff,
                         spill2_coil_field * shutoff,
                         adwin_ramp_sampling_rate, units='G')
    
    spill_start = t + spill2_start + spill2_coil_ramp
    Mixer_Tweezer.ramp(spill_start, spill2_tweezer_ramp,
                       tweezer_evap_end, spill2_tweezer_depth,
                       adwin_ramp_sampling_rate)
    
    ramp_back_start = spill_start + spill2_tweezer_ramp + spill2_hold
    Mixer_Tweezer.ramp(ramp_back_start, spill2_tweezer_ramp,
                       spill2_tweezer_depth, tweezer_evap_end,
                       adwin_ramp_sampling_rate)
    
    grad_off_start = ramp_back_start + spill2_tweezer_ramp
    Coil_L1.ramp(grad_off_start, spill2_coil_ramp, spill2_coil_grad, 0, adwin_ramp_sampling_rate)
    Coil_R2.ramp(grad_off_start, spill2_coil_ramp, spill2_coil_grad, 0, adwin_ramp_sampling_rate)
    
    # Letzte Aktion: Coil ramps enden
    return grad_off_start + spill2_coil_ramp

# =============================================================================
# Block 26: Spilling Imbalance (Block Active = FALSE)
# =============================================================================
def spilling_imbalance(t):
    """Spilling with imbalanced tweezer for asymmetric preparation"""
    
    Switch_Coil_R2.go_high(t + spill_imb_start - 20*ms)
    Switch_Coil_L1.go_high(t + spill_imb_start - 20*ms)
    
    Coil_L1.ramp(t + spill_imb_start, spill_imb_coil_ramp, 0, spill_imb_coil_grad_l, adwin_ramp_sampling_rate)
    Coil_R2.ramp(t + spill_imb_start, spill_imb_coil_ramp, 0, spill_imb_coil_grad_r, adwin_ramp_sampling_rate)
    
    Coil_R1_plus_L2.ramp(t + spill_imb_start - 20*ms, spill_imb_coil_ramp,
                         spill1_coil_field * shutoff,
                         spill_imb_coil_field * shutoff,
                         adwin_ramp_sampling_rate, units='G')
    
    spill_start = t + spill_imb_start + spill_imb_coil_ramp
    Mixer_Tweezer.ramp(spill_start, spill_imb_tweezer_ramp,
                       tweezer_evap_end, spill_imb_tweezer_depth,
                       adwin_ramp_sampling_rate)
    
    ramp_back_start = spill_start + spill_imb_tweezer_ramp + spill_imb_hold
    Mixer_Tweezer.ramp(ramp_back_start, spill_imb_tweezer_ramp,
                       spill_imb_tweezer_depth, tweezer_evap_end,
                       adwin_ramp_sampling_rate)
    
    grad_off_start = ramp_back_start + spill_imb_tweezer_ramp
    Coil_L1.ramp(grad_off_start, spill_imb_coil_ramp, spill_imb_coil_grad_l, 0, adwin_ramp_sampling_rate)
    Coil_R2.ramp(grad_off_start, spill_imb_coil_ramp, spill_imb_coil_grad_r, 0, adwin_ramp_sampling_rate)
    
    # Letzte Aktion: Coil ramps enden
    return grad_off_start + spill_imb_coil_ramp

# =============================================================================
# Block 27: Spilling 3 (Block Active = FALSE)
# =============================================================================
def spilling_3(t):
    """Third spilling sequence"""
    
    Coil_L1.ramp(t + spill3_start, spill3_coil_ramp, 0, spill3_coil_grad, adwin_ramp_sampling_rate)
    Coil_R2.ramp(t + spill3_start, spill3_coil_ramp, 0, spill3_coil_grad, adwin_ramp_sampling_rate)
    
    Coil_R1_plus_L2.ramp(t + spill3_start - 20*ms, spill3_coil_ramp,
                         spill2_coil_field * shutoff,
                         spill3_coil_field * shutoff,
                         adwin_ramp_sampling_rate, units='G')
    
    spill_start = t + spill3_start + spill3_coil_ramp
    Mixer_Tweezer.ramp(spill_start, spill3_tweezer_ramp,
                       tweezer_evap_end, spill3_tweezer_depth,
                       adwin_ramp_sampling_rate)
    
    ramp_back_start = spill_start + spill3_tweezer_ramp + spill3_hold
    Mixer_Tweezer.ramp(ramp_back_start, spill3_tweezer_ramp,
                       spill3_tweezer_depth, tweezer_evap_end,
                       adwin_ramp_sampling_rate)
    
    grad_off_start = ramp_back_start + spill3_tweezer_ramp
    Coil_L1.ramp(grad_off_start, spill3_coil_ramp, spill3_coil_grad, 0, adwin_ramp_sampling_rate)
    Coil_R2.ramp(grad_off_start, spill3_coil_ramp, spill3_coil_grad, 0, adwin_ramp_sampling_rate)
    
    # Letzte Aktion: Coil ramps enden
    return grad_off_start + spill3_coil_ramp

# =============================================================================
# Block 28: Spilling 4 (Block Active = FALSE)
# =============================================================================
def spilling_4(t):
    """Fourth spilling sequence"""
    
    Coil_L1.ramp(t + spill4_start, spill4_coil_ramp, 0, spill4_coil_grad, adwin_ramp_sampling_rate)
    Coil_R2.ramp(t + spill4_start, spill4_coil_ramp, 0, spill4_coil_grad, adwin_ramp_sampling_rate)
    
    Coil_R1_plus_L2.ramp(t + spill4_start - 20*ms, spill4_coil_ramp,
                         spill3_coil_field * shutoff,
                         spill4_coil_field * shutoff,
                         adwin_ramp_sampling_rate, units='G')
    
    spill_start = t + spill4_start + spill4_coil_ramp
    Mixer_Tweezer.ramp(spill_start, spill4_tweezer_ramp,
                       tweezer_evap_end, spill4_tweezer_depth,
                       adwin_ramp_sampling_rate)
    
    ramp_back_start = spill_start + spill4_tweezer_ramp + spill4_hold
    Mixer_Tweezer.ramp(ramp_back_start, spill4_tweezer_ramp,
                       spill4_tweezer_depth, tweezer_evap_end,
                       adwin_ramp_sampling_rate)
    
    grad_off_start = ramp_back_start + spill4_tweezer_ramp
    Coil_L1.ramp(grad_off_start, spill4_coil_ramp, spill4_coil_grad, 0, adwin_ramp_sampling_rate)
    Coil_R2.ramp(grad_off_start, spill4_coil_ramp, spill4_coil_grad, 0, adwin_ramp_sampling_rate)
    
    # Letzte Aktion: Coil ramps enden
    return grad_off_start + spill4_coil_ramp

# =============================================================================
# Block 29: Spilling 5 (Block Active = FALSE)
# =============================================================================
def spilling_5(t):
    """Fifth spilling sequence"""
    
    Coil_L1.ramp(t + spill5_start, spill5_coil_ramp, 0, spill5_coil_grad, adwin_ramp_sampling_rate)
    Coil_R2.ramp(t + spill5_start, spill5_coil_ramp, 0, spill5_coil_grad, adwin_ramp_sampling_rate)
    
    Coil_R1_plus_L2.ramp(t + spill5_start - 20*ms, spill5_coil_ramp,
                         spill4_coil_field * shutoff,
                         spill5_coil_field * shutoff,
                         adwin_ramp_sampling_rate, units='G')
    
    spill_start = t + spill5_start + spill5_coil_ramp
    Mixer_Tweezer.ramp(spill_start, spill5_tweezer_ramp,
                       tweezer_evap_end, spill5_tweezer_depth,
                       adwin_ramp_sampling_rate)
    
    ramp_back_start = spill_start + spill5_tweezer_ramp + spill5_hold
    Mixer_Tweezer.ramp(ramp_back_start, spill5_tweezer_ramp,
                       spill5_tweezer_depth, tweezer_evap_end,
                       adwin_ramp_sampling_rate)
    
    grad_off_start = ramp_back_start + spill5_tweezer_ramp
    Coil_L1.ramp(grad_off_start, spill5_coil_ramp, spill5_coil_grad, 0, adwin_ramp_sampling_rate)
    Coil_R2.ramp(grad_off_start, spill5_coil_ramp, spill5_coil_grad, 0, adwin_ramp_sampling_rate)
    
    # Letzte Aktion: Coil ramps enden
    return grad_off_start + spill5_coil_ramp

# =============================================================================
# Block 30: 808 Tweezer (Block Active = FALSE)
# =============================================================================
def tweezer_808(t):
    """808nm Tweezer loading sequence"""
    
    # Activate 808nm Tweezer PID
    Mixer_808_Tweezer.set_PID(t + tw808_start - aom_on_delay, Photodiode_808_Tweezer_Gain50, set_output=0)
    
    Shutter_808.go_high(t + tw808_start)
    Shutter_Tweezer.go_low(t + tw808_start - tw808_pre_shutter)
    
    Mixer_808_Tweezer.constant(t + tw808_start - aom_on_delay, 0)
    Mixer_808_Tweezer.ramp(t + tw808_start, tw808_power_ramp,
                           0, tw808_power_initial, adwin_ramp_sampling_rate)
    
    Mixer_808_Tweezer.ramp(t + tw808_start + tw808_power_ramp, tw808_evap_time,
                           tw808_power_initial, tw808_evap_end, adwin_ramp_sampling_rate)
    
    Mixer_Tweezer.constant(t + tw808_start - tw808_pre_shutter, 0)
    
    # Letzte Aktion: Mixer_808_Tweezer evap ramp endet
    return t + tw808_start + tw808_power_ramp + tw808_evap_time

# =============================================================================
# Block 31: 808 Spilling 1 (Block Active = FALSE)
# =============================================================================
def spilling_808_1(t):
    """808nm Tweezer first spilling sequence"""
    
    Switch_Coil_R2.go_high(t + spill808_1_start - 20*ms)
    Switch_Coil_L1.go_high(t + spill808_1_start - 20*ms)
    
    Coil_L1.ramp(t + spill808_1_start, spill808_1_coil_ramp, 0, spill808_1_coil_grad, adwin_ramp_sampling_rate)
    Coil_R2.ramp(t + spill808_1_start, spill808_1_coil_ramp, 0, spill808_1_coil_grad, adwin_ramp_sampling_rate)
    
    Coil_R1_plus_L2.ramp(t + spill808_1_start - 20*ms, spill808_1_coil_ramp,
                         spill1_coil_field * shutoff,
                         spill808_1_coil_field * shutoff,
                         adwin_ramp_sampling_rate, units='G')
    
    spill_start = t + spill808_1_start + spill808_1_coil_ramp
    Mixer_808_Tweezer.ramp(spill_start, spill808_1_tweezer_ramp,
                           tw808_evap_end, spill808_1_tweezer_depth, adwin_ramp_sampling_rate)
    
    ramp_back_start = spill_start + spill808_1_tweezer_ramp + spill808_1_hold
    Mixer_808_Tweezer.ramp(ramp_back_start, spill808_1_tweezer_ramp,
                           spill808_1_tweezer_depth, tw808_evap_end, adwin_ramp_sampling_rate)
    
    grad_off_start = ramp_back_start + spill808_1_tweezer_ramp
    Coil_L1.ramp(grad_off_start, spill808_1_coil_ramp, spill808_1_coil_grad, 0, adwin_ramp_sampling_rate)
    Coil_R2.ramp(grad_off_start, spill808_1_coil_ramp, spill808_1_coil_grad, 0, adwin_ramp_sampling_rate)
    
    # Letzte Aktion: Coil ramps enden
    return grad_off_start + spill808_1_coil_ramp

# =============================================================================
# Block 32: 808 Modulation (Block Active = FALSE)
# =============================================================================
def modulation_808(t):
    """808nm Tweezer modulation for parametric excitation"""
    
    DOUT_Channel29.trigger(t + tw808_mod_start, 0.02*ms)
    
    # Sinusoidal modulation on Mixer_808_Tweezer
    # modulation_depth = tw808_mod_depth, period = tw808_mod_period
    
    # Letzte Aktion: DOUT_Channel29 trigger
    return t + tw808_mod_start + 0.02*ms

# =============================================================================
# Block 33: 808 Spilling 2 (Block Active = FALSE)
# =============================================================================
def spilling_808_2(t):
    """808nm Tweezer second spilling sequence"""
    
    Coil_L1.ramp(t + spill808_2_start, spill808_2_coil_ramp, 0, spill808_2_coil_grad, adwin_ramp_sampling_rate)
    Coil_R2.ramp(t + spill808_2_start, spill808_2_coil_ramp, 0, spill808_2_coil_grad, adwin_ramp_sampling_rate)
    
    Coil_R1_plus_L2.ramp(t + spill808_2_start - 20*ms, spill808_2_coil_ramp,
                         spill808_1_coil_field * shutoff,
                         spill808_2_coil_field * shutoff,
                         adwin_ramp_sampling_rate, units='G')
    
    spill_start = t + spill808_2_start + spill808_2_coil_ramp
    Mixer_808_Tweezer.ramp(spill_start, spill808_2_tweezer_ramp,
                           tw808_evap_end, spill808_2_tweezer_depth, adwin_ramp_sampling_rate)
    
    ramp_back_start = spill_start + spill808_2_tweezer_ramp + spill808_2_hold
    Mixer_808_Tweezer.ramp(ramp_back_start, spill808_2_tweezer_ramp,
                           spill808_2_tweezer_depth, tw808_evap_end, adwin_ramp_sampling_rate)
    
    grad_off_start = ramp_back_start + spill808_2_tweezer_ramp
    Coil_L1.ramp(grad_off_start, spill808_2_coil_ramp, spill808_2_coil_grad, 0, adwin_ramp_sampling_rate)
    Coil_R2.ramp(grad_off_start, spill808_2_coil_ramp, spill808_2_coil_grad, 0, adwin_ramp_sampling_rate)
    
    # Letzte Aktion: Coil ramps enden
    return grad_off_start + spill808_2_coil_ramp

# =============================================================================
# Block 34: Tunnelling (Block Active = FALSE)
# =============================================================================
def tunnelling(t):
    """Tunnelling dynamics sequence for studying inter-site tunnelling"""
    
    Shutter_808.go_high(t + tunnel_start)
    
    Mixer_808_Tweezer.ramp(t + tunnel_start, tunnel_ramp,
                           tw808_evap_end, tunnel_power_808, adwin_ramp_sampling_rate)
    
    Mixer_Tweezer.ramp(t + tunnel_start, tunnel_ramp,
                       tweezer_evap_end, tunnel_power_1064, adwin_ramp_sampling_rate)
    
    Mixer_808_Tweezer.ramp(t + tunnel_start + tunnel_ramp + tunnel_time, tunnel_ramp,
                           tunnel_power_808, tw808_evap_end, adwin_ramp_sampling_rate)
    Mixer_Tweezer.ramp(t + tunnel_start + tunnel_ramp + tunnel_time, tunnel_ramp,
                       tunnel_power_1064, tweezer_evap_end, adwin_ramp_sampling_rate)
    
    Coil_R1_plus_L2.ramp(t + tunnel_start - 10*ms, 10*ms,
                         spill1_coil_field * shutoff,
                         tunnel_coil_field * shutoff,
                         adwin_ramp_sampling_rate, units='G')
    
    Coil_L1.ramp(t + tunnel_start, tunnel_ramp, 0, tunnel_coil_grad, adwin_ramp_sampling_rate, units='G')
    Coil_R2.ramp(t + tunnel_start, tunnel_ramp, 0, tunnel_coil_grad, adwin_ramp_sampling_rate, units='G')
    
    # Letzte Aktion: Tweezer ramps back enden
    return t + tunnel_start + tunnel_ramp + tunnel_time + tunnel_ramp

# =============================================================================
# Block 35: Vacuum meas (Block Active = FALSE)
# =============================================================================
def vacuum_measurement(t):
    """Vacuum lifetime measurement sequence"""
    
    Mixer_Tweezer.constant(t, tweezer_evap_end)
    Mixer_808_Tweezer.constant(t, tw808_evap_end)
    Coil_R1_plus_L2.constant(t, spill1_coil_field * shutoff, units='G')
    
    # Alle Aktionen bei t - keine Zeitfortschritt
    return t

# =============================================================================
# Block 36: Microwave (Block Active = FALSE)
# =============================================================================
def microwave(t):
    """Microwave pulse sequence for spin manipulation"""
    
    Switch_Microwave.trigger(t + mw_start, mw_time)
    DOUT_Channel60.trigger(t + mw_start - 1*ms, mw_time + 2*ms)
    
    Coil_R1_plus_L2.ramp(t + mw_start - 20*ms, 10*ms,
                         flash_coil23 * shutoff,
                         mw_coil_field * shutoff,
                         adwin_ramp_sampling_rate, units='G')
    
    Coil_R1_plus_L2.ramp(t + mw_start + mw_time, 10*ms,
                         mw_coil_field * shutoff,
                         flash_coil23 * shutoff,
                         adwin_ramp_sampling_rate, units='G')
    
    # Letzte Aktion: Coil_R1_plus_L2 ramp back endet
    return t + mw_start + mw_time + 10*ms

# =============================================================================
# Block 1: Logging (Block Active = TRUE)
# =============================================================================
def logging(t):
    """Trigger logging during MOT loading"""
    Trigger_MOT_Logging.trigger(t, trigger_duration)
    # Letzte Aktion: Trigger endet bei t + trigger_duration
    return t + trigger_duration
