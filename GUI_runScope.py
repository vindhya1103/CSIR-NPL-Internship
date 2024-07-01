import PySimpleGUI as sg
from RsInstrument import RsInstrument
import os
import pyvisa
import math
import csv

SIZE_X = 200
SIZE_Y = 100
NUMBER_MARKER_FREQ = SIZE_X // 8
AMPLITUDE = SIZE_Y // 2
FREQUENCY = 0.1
PHASE_SHIFT_SPEED = 0.1

rm = pyvisa.ResourceManager()

os_address = ""  # Provide the correct address for the oscilloscope
# sig_gen_address = ""  # Provide the correct address for the signal generator
# sig_gen = rm.open_resource(sig_gen_address)

try:
    oscilloscope = RsInstrument(os_address)
except Exception as e:
    print(f"error init oscilloscope: {e}")

# GUI layout
oscilloscope_tab_layout = [
    [
        sg.Button("Capture Screenshot"),
        sg.Button("Transfer Waveform"),
        sg.Button("Show oscilloscope waveform"),
    ],
    [sg.Text("Select Channel:"), sg.Combo(["CH1", "CH2", "CH3"], key="-CHANNEL-")],
    [sg.Text("Set Horizontal scale"), sg.Stretch(), sg.Text("Set Vertical scale")],
    [
        sg.Slider(range=(0, 10), default_value=5, orientation="h", key="-HORIZONTAL-"),
        sg.Slider(range=(0, 10), default_value=5, orientation="h", key="-VERTICAL-"),
    ],
    [sg.Button("Auto"), sg.Button("Normal"), sg.Button("Single")],
    [sg.Multiline(size=(30, 3), key="-OSC_DETAILS-", disabled=True)],
    [
        sg.Slider(
            (0, SIZE_Y),
            orientation="h",
            enable_events=True,
            key="_SLIDER_1",
            expand_x=True,
        )
    ],
    [
        sg.Slider(
            (0, SIZE_Y),
            orientation="h",
            enable_events=True,
            key="_SLIDER_2",
            expand_x=True,
        )
    ],
]

# Define the layout for the Signal Generator Controls Tab
signal_generator_tab_layout = [
    [sg.Text("Frequency (Hz):"), sg.InputText(key="-FREQ-")],
    [sg.Text("Power Level (dBm):"), sg.InputText(key="-POWER-")],
    [sg.Button("Start Signal"), sg.Button("Stop Signal")],
    [
        sg.Text("Select Waveform Type:"),
        sg.Combo(["Sine", "Square", "Triangle"], key="-WAVEFORM_TYPE-"),
    ],
]

# Create the main layout with tabs
layout = [
    [
        sg.TabGroup(
            [
                [sg.Tab("Oscilloscope Controls", oscilloscope_tab_layout)],
                # [graph_frame],
                [sg.Tab("Signal Generator Controls", signal_generator_tab_layout)],
            ]
        )
    ],
    [sg.Button("Exit")],
]
# Create the window
window = sg.Window(
    "Instrument Automation", layout, resizable=True, element_justification="center"
)


def create_waveform_data():
    waveform_data = [[t, 5 * math.sin(0.1 * t) + 5] for t in range(100)]
    return waveform_data


def show_waveform_data_as_table(waveform_data):
    layout = [
        [
            sg.Table(
                values=waveform_data,
                headings=["Time", "Voltage"],
                display_row_numbers=True,
                auto_size_columns=True,
                num_rows=min(25, len(waveform_data)),
            )
        ]
    ]
    window = sg.Window("Waveform Data", layout)
    event, values = window.read()
    window.close()


def plot_real_time_oscilloscope():
    SIZE_X = 200
    SIZE_Y = 100
    AMPLITUDE = SIZE_Y // 2
    FREQUENCY = 0.1
    PHASE_SHIFT_SPEED = 0.1

    # GUI layout
    layout = [
        [
            sg.Graph(
                canvas_size=(800, 400),
                graph_bottom_left=(-SIZE_X, -SIZE_Y),
                graph_top_right=(SIZE_X, SIZE_Y),
                background_color="black",
                key="-GRAPH-",
            )
        ],
        [
            sg.Text("Time Axis:"),
            sg.Slider(range=(0, 100), default_value=0, orientation="h", key="-TIME-"),
            sg.Text("Offset:"),
            sg.Slider(
                range=(-SIZE_Y, SIZE_Y),
                default_value=0,
                orientation="h",
                key="-OFFSET-",
            ),
            sg.Text("Channel:"),
            sg.Combo(
                ["CH1", "CH2", "CH3", "All"], default_value="CH1", key="-CHANNEL-"
            ),
            sg.Text("Concurrency:"),
            sg.Radio("Active", "CONCURRENCY", default=True, key="-ACTIVE-"),
            sg.Radio("Inactive", "CONCURRENCY", key="-INACTIVE-"),
        ],
        [sg.Button("Exit")],
    ]

    # Create the window
    window = sg.Window("Real-Time Oscilloscope", layout, finalize=True)

    # Function to draw the sine wave
    def draw_sine_wave(graph, amplitude, frequency, phase_shift):
        graph.erase()
        draw_axis(graph)  # Draw axes
        prev_x = prev_y = None
        for x in range(-SIZE_X, SIZE_X):
            y = amplitude * math.sin(
                frequency * (x * 2 * math.pi / SIZE_X) + phase_shift
            )
            if prev_x is not None:
                graph.draw_line((prev_x, prev_y), (x, y), color="yellow")
            prev_x, prev_y = x, y

    # Function to draw the axes
    def draw_axis(graph):
        graph.draw_line((-SIZE_X, 0), (SIZE_X, 0), color="white")  # X-axis
        graph.draw_line((0, -SIZE_Y), (0, SIZE_Y), color="white")  # Y-axis

    phase_shift = 0

    # Event loop
    while True:
        event, values = window.read(timeout=100)  # Update every 100 milliseconds
        if event == sg.WINDOW_CLOSED or event == "Exit":
            break
        amplitude = AMPLITUDE
        frequency = FREQUENCY
        channel = values["-CHANNEL-"]
        if channel == "All":
            for ch in ["CH1", "CH2", "CH3"]:
                draw_sine_wave(window["-GRAPH-"], amplitude, frequency, phase_shift)
                amplitude -= 10  # Offset amplitude for multiple channels
                frequency += 0.05  # Offset frequency for multiple channels
        else:
            draw_sine_wave(window["-GRAPH-"], amplitude, frequency, phase_shift)
        phase_shift += PHASE_SHIFT_SPEED

    # Close the window
    window.close()


def PopUp_SS(pc_path):
    answer = sg.popup_yes_no("Screenshot captured. Would you like to view it?")
    if answer == "Yes":
        if os.path.exists(pc_path):
            screenshot_layout = [
                [sg.Image(filename=pc_path)],
                [sg.Button("Close")],
            ]
            screenshot_window = sg.Window("Screenshot", screenshot_layout)
            while True:
                screenshot_event, _ = screenshot_window.read()
                if screenshot_event == sg.WIN_CLOSED or screenshot_event == "Close":
                    screenshot_window.close()
                    break
        else:
            sg.popup_error("Screenshot file not found.")


# Event loop
while True:
    event, values = window.read()
    pc_path = "C:\\Users\\Vindhya Sree\\OneDrive\\Desktop\\CSIR\\GUI_Images\\GUI2.png"
    waveform_filename = (
        "C:\\Users\\Vindhya Sree\\OneDrive\\Desktop\\CSIR\\CSVs\\WFM02.CSV"
    )
    if event == sg.WIN_CLOSED or event == "Exit":
        break
    elif event == "Capture Screenshot":
        PopUp_SS(pc_path)
    elif event == "Transfer Waveform":
        waveform_data = create_waveform_data()
        show_waveform_data_as_table(waveform_data)
        sg.popup("Waveform data transferred to PC.")
        # oscilloscope.write_str_with_opc("FORM REAL,32")
        # oscilloscope.write_str_with_opc("CHAN1:DATA?")
        # waveform_data = oscilloscope.read_bin_float_data()
    elif event == "Show oscilloscope waveform":
        plot_real_time_oscilloscope()
    elif event == "Set Frequency and Power":
        frequency = values["frequency"]
        power = values["power"]
        # SCPI command to instrument that sets freq and power level.
        # sig_gen.write(f"SOUR:FREQ {frequency}MHz")
        # sig_gen.write(f"SOUR:POW {power} dBm")
        sg.popup(
            f"Frequency set to {frequency} MHz and Power to {power} dBm",
            size=(400, 150),
        )
    elif event == "Set Trigger":
        # oscilloscope.write_str_with_opc("TRIGger:MODE LEVel")
        # oscilloscope.write_str_with_opc("TRIGger:LEVel:SOURce CHANnel1")
        # oscilloscope.write_str_with_opc("TRIGger:LEVel CHANnel1,0.5")
        sg.popup("Trigger set on oscilloscope.", size=(400, 150))
    elif event == "Set FFT":
        # oscilloscope.write_str_with_opc("CALCulate:FFT:WINDow HANNing")
        # oscilloscope.write_str_with_opc("CALCulate:FFT:SOURce CHANnel1")
        # oscilloscope.write_str_with_opc("DISPlay:FFT:WINDow:STATe ON")
        sg.popup("FFT set on oscilloscope.", size=(400, 150))

# Close the window
window.close()
