# GitHub examples repository path: Oscilloscopes/Python/RsInstrument
# Example for RTM3004 Oscilloscope
# Preconditions:
# - Installed RsInstrument Python module from pypi.org
# - Installed VISA e.g. R&S Visa 5.12.x or newer

from RsInstrument import *
from time import time

# Make sure you have the latest version of the RsInstrument
RsInstrument.assert_minimum_version('1.53.0')

try:
    rtm = RsInstrument('TCPIP::169.254.16.237::INSTR', True, False)
    rtm.visa_timeout = 3000
    rtm.opc_timeout = 15000
    rtm.instrument_status_checking = True
except Exception as ex:
    print(f'Error initializing the instrument session:\n{ex.args[0]}')
    exit()

print(f'RTM3004 IDN: {rtm.idn_string}')
print(f'RTM3004 Options: {",".join(rtm.instrument_options)}')

rtm.clear_status()
rtm.reset()
#rtm.write_str("SYST:DISP:UPD ON")  # Enable display update (switch OFF after debugging)

# Basic Settings:
rtm.write_str("ACQ:POIN:AUTO ON")  # Enable automatic acquisition points *not working in RTO2044
rtm.write_str("TIM:RANG 0.01")  # 10 ms Acquisition time
rtm.write_str("ACQ:POIN 20002")  # 20002 X points      *not working in RTO2044
rtm.write_str("CHAN1:RANG 2")  # Horizontal range 2V
rtm.write_str("CHAN1:POS 0")  # Offset 0
rtm.write_str("CHAN1:COUP AC")  # Coupling AC 1MOhm
rtm.write_str("CHAN1:STAT ON")  # Switch Channel 1 ON

# Trigger Settings:
rtm.write_str("TRIG1:MODE AUTO")  # Trigger Auto mode
rtm.write_str("TRIG1:SOUR CHAN1")  # Trigger source CH1
rtm.write_str("TRIG1:TYPE EDGE;:TRIG1:EDGE:SLOP POS")  # Trigger type Edge Positive
rtm.write_str("TRIG1:LEV1 0.04")  # Trigger level 40mV
rtm.query_opc()  # Wait until all instrument settings are finished

# Arming the RTM for single acquisition
rtm.visa_timeout = 2000  # Set acquisition timeout higher than the acquisition time
rtm.write_str("SING")

# Wait for acquisition to finish
rtm.query_opc()

# Fetch the waveform in ASCII and binary format
t = time()
trace_ascii = rtm.query_bin_or_ascii_float_list('FORM ASC;:CHAN1:DATA?')  # Query ASCII array of floats
print(f'Instrument returned {len(trace_ascii)} points in the ASCII trace, query duration {time() - t:.3f} secs')

t = time()
rtm.bin_float_numbers_format = BinFloatFormat.Single_4bytes #not working in RTO2044
trace_binary = rtm.query_bin_or_ascii_float_list('FORM REAL,32;:CHAN1:DATA?')  # Query binary array of floats
print(f'Instrument returned {len(trace_binary)} points in the binary trace, query duration {time() - t:.3f} secs')

# Capture a screenshot and transfer the file to the PC
rtm.write_str('HCOP:DEV:LANG PNG')  # Set the screenshot format
rtm.write_str(r"MMEM:NAME 'c:\temp\Dev_Screenshot.png'")  # Set the screenshot path
rtm.write_str("HCOP:IMM")  # Capture the screenshot
rtm.query_opc()  # Wait for the screenshot to be saved
rtm.read_file_from_instrument_to_pc(r'c:\temp\Dev_Screenshot.png', r'c:\Temp\PC_Screenshot.png')  # Transfer the file
print(r"Screenshot file saved to PC 'c:\Temp\PC_Screenshot.png'")

# Close the session
rtm.close()