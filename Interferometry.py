#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Interferometry
# Author: SETI Institute
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
from gnuradio import blocks
from gnuradio import channels
from gnuradio.filter import firdes
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio.filter import pfb
import numpy as np
import sip
import threading



class Interferometry(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Interferometry", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Interferometry")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "Interferometry")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.snr = snr = 0
        self.samp_rate = samp_rate = 1000000
        self.phase_diff_3 = phase_diff_3 = 0
        self.phase_diff_2 = phase_diff_2 = 0
        self.phase_diff = phase_diff = 0
        self.frequency = frequency = 50
        self.freq_diff_3 = freq_diff_3 = 0
        self.freq_diff_2 = freq_diff_2 = 0
        self.freq_diff = freq_diff = 0
        self.delay_rate_diff_3 = delay_rate_diff_3 = 0
        self.delay_rate_diff_2 = delay_rate_diff_2 = 0
        self.delay_rate_diff = delay_rate_diff = 0
        self.delay_diff_3 = delay_diff_3 = 0
        self.delay_diff_2 = delay_diff_2 = 0
        self.delay_diff = delay_diff = 0
        self.bandwidth = bandwidth = 100

        ##################################################
        # Blocks
        ##################################################

        self._snr_tool_bar = Qt.QToolBar(self)
        self._snr_tool_bar.addWidget(Qt.QLabel("Signal to Noise Ratio (SNR)" + ": "))
        self._snr_line_edit = Qt.QLineEdit(str(self.snr))
        self._snr_tool_bar.addWidget(self._snr_line_edit)
        self._snr_line_edit.editingFinished.connect(
            lambda: self.set_snr(eng_notation.str_to_num(str(self._snr_line_edit.text()))))
        self.top_layout.addWidget(self._snr_tool_bar)
        self._phase_diff_3_tool_bar = Qt.QToolBar(self)
        self._phase_diff_3_tool_bar.addWidget(Qt.QLabel("Phase difference (deg) (ANT4)" + ": "))
        self._phase_diff_3_line_edit = Qt.QLineEdit(str(self.phase_diff_3))
        self._phase_diff_3_tool_bar.addWidget(self._phase_diff_3_line_edit)
        self._phase_diff_3_line_edit.editingFinished.connect(
            lambda: self.set_phase_diff_3(eng_notation.str_to_num(str(self._phase_diff_3_line_edit.text()))))
        self.top_layout.addWidget(self._phase_diff_3_tool_bar)
        self._phase_diff_2_tool_bar = Qt.QToolBar(self)
        self._phase_diff_2_tool_bar.addWidget(Qt.QLabel("Phase difference (deg) (ANT3)" + ": "))
        self._phase_diff_2_line_edit = Qt.QLineEdit(str(self.phase_diff_2))
        self._phase_diff_2_tool_bar.addWidget(self._phase_diff_2_line_edit)
        self._phase_diff_2_line_edit.editingFinished.connect(
            lambda: self.set_phase_diff_2(eng_notation.str_to_num(str(self._phase_diff_2_line_edit.text()))))
        self.top_layout.addWidget(self._phase_diff_2_tool_bar)
        self._phase_diff_tool_bar = Qt.QToolBar(self)
        self._phase_diff_tool_bar.addWidget(Qt.QLabel("Phase difference (deg) (ANT2)" + ": "))
        self._phase_diff_line_edit = Qt.QLineEdit(str(self.phase_diff))
        self._phase_diff_tool_bar.addWidget(self._phase_diff_line_edit)
        self._phase_diff_line_edit.editingFinished.connect(
            lambda: self.set_phase_diff(eng_notation.str_to_num(str(self._phase_diff_line_edit.text()))))
        self.top_layout.addWidget(self._phase_diff_tool_bar)
        self._frequency_tool_bar = Qt.QToolBar(self)
        self._frequency_tool_bar.addWidget(Qt.QLabel("Signal frequency (kHz)" + ": "))
        self._frequency_line_edit = Qt.QLineEdit(str(self.frequency))
        self._frequency_tool_bar.addWidget(self._frequency_line_edit)
        self._frequency_line_edit.editingFinished.connect(
            lambda: self.set_frequency(eng_notation.str_to_num(str(self._frequency_line_edit.text()))))
        self.top_layout.addWidget(self._frequency_tool_bar)
        self._freq_diff_3_tool_bar = Qt.QToolBar(self)
        self._freq_diff_3_tool_bar.addWidget(Qt.QLabel("Frequency difference (Hz) (ANT4)" + ": "))
        self._freq_diff_3_line_edit = Qt.QLineEdit(str(self.freq_diff_3))
        self._freq_diff_3_tool_bar.addWidget(self._freq_diff_3_line_edit)
        self._freq_diff_3_line_edit.editingFinished.connect(
            lambda: self.set_freq_diff_3(eng_notation.str_to_num(str(self._freq_diff_3_line_edit.text()))))
        self.top_layout.addWidget(self._freq_diff_3_tool_bar)
        self._freq_diff_2_tool_bar = Qt.QToolBar(self)
        self._freq_diff_2_tool_bar.addWidget(Qt.QLabel("Frequency difference (Hz) (ANT3)" + ": "))
        self._freq_diff_2_line_edit = Qt.QLineEdit(str(self.freq_diff_2))
        self._freq_diff_2_tool_bar.addWidget(self._freq_diff_2_line_edit)
        self._freq_diff_2_line_edit.editingFinished.connect(
            lambda: self.set_freq_diff_2(eng_notation.str_to_num(str(self._freq_diff_2_line_edit.text()))))
        self.top_layout.addWidget(self._freq_diff_2_tool_bar)
        self._freq_diff_tool_bar = Qt.QToolBar(self)
        self._freq_diff_tool_bar.addWidget(Qt.QLabel("Frequency difference (Hz) (ANT2)" + ": "))
        self._freq_diff_line_edit = Qt.QLineEdit(str(self.freq_diff))
        self._freq_diff_tool_bar.addWidget(self._freq_diff_line_edit)
        self._freq_diff_line_edit.editingFinished.connect(
            lambda: self.set_freq_diff(eng_notation.str_to_num(str(self._freq_diff_line_edit.text()))))
        self.top_layout.addWidget(self._freq_diff_tool_bar)
        self._delay_rate_diff_3_tool_bar = Qt.QToolBar(self)
        self._delay_rate_diff_3_tool_bar.addWidget(Qt.QLabel("Delay rate difference (ppm) (ANT4)" + ": "))
        self._delay_rate_diff_3_line_edit = Qt.QLineEdit(str(self.delay_rate_diff_3))
        self._delay_rate_diff_3_tool_bar.addWidget(self._delay_rate_diff_3_line_edit)
        self._delay_rate_diff_3_line_edit.editingFinished.connect(
            lambda: self.set_delay_rate_diff_3(eng_notation.str_to_num(str(self._delay_rate_diff_3_line_edit.text()))))
        self.top_layout.addWidget(self._delay_rate_diff_3_tool_bar)
        self._delay_rate_diff_2_tool_bar = Qt.QToolBar(self)
        self._delay_rate_diff_2_tool_bar.addWidget(Qt.QLabel("Delay rate difference (ppm) (ANT3)" + ": "))
        self._delay_rate_diff_2_line_edit = Qt.QLineEdit(str(self.delay_rate_diff_2))
        self._delay_rate_diff_2_tool_bar.addWidget(self._delay_rate_diff_2_line_edit)
        self._delay_rate_diff_2_line_edit.editingFinished.connect(
            lambda: self.set_delay_rate_diff_2(eng_notation.str_to_num(str(self._delay_rate_diff_2_line_edit.text()))))
        self.top_layout.addWidget(self._delay_rate_diff_2_tool_bar)
        self._delay_rate_diff_tool_bar = Qt.QToolBar(self)
        self._delay_rate_diff_tool_bar.addWidget(Qt.QLabel("Delay rate difference (ppm) (ANT2)" + ": "))
        self._delay_rate_diff_line_edit = Qt.QLineEdit(str(self.delay_rate_diff))
        self._delay_rate_diff_tool_bar.addWidget(self._delay_rate_diff_line_edit)
        self._delay_rate_diff_line_edit.editingFinished.connect(
            lambda: self.set_delay_rate_diff(eng_notation.str_to_num(str(self._delay_rate_diff_line_edit.text()))))
        self.top_layout.addWidget(self._delay_rate_diff_tool_bar)
        self._delay_diff_3_tool_bar = Qt.QToolBar(self)
        self._delay_diff_3_tool_bar.addWidget(Qt.QLabel("Delay difference (samples) (ANT4)" + ": "))
        self._delay_diff_3_line_edit = Qt.QLineEdit(str(self.delay_diff_3))
        self._delay_diff_3_tool_bar.addWidget(self._delay_diff_3_line_edit)
        self._delay_diff_3_line_edit.editingFinished.connect(
            lambda: self.set_delay_diff_3(int(str(self._delay_diff_3_line_edit.text()))))
        self.top_layout.addWidget(self._delay_diff_3_tool_bar)
        self._delay_diff_2_tool_bar = Qt.QToolBar(self)
        self._delay_diff_2_tool_bar.addWidget(Qt.QLabel("Delay difference (samples) (ANT3)" + ": "))
        self._delay_diff_2_line_edit = Qt.QLineEdit(str(self.delay_diff_2))
        self._delay_diff_2_tool_bar.addWidget(self._delay_diff_2_line_edit)
        self._delay_diff_2_line_edit.editingFinished.connect(
            lambda: self.set_delay_diff_2(int(str(self._delay_diff_2_line_edit.text()))))
        self.top_layout.addWidget(self._delay_diff_2_tool_bar)
        self._delay_diff_tool_bar = Qt.QToolBar(self)
        self._delay_diff_tool_bar.addWidget(Qt.QLabel("Delay difference (samples) (ANT2)" + ": "))
        self._delay_diff_line_edit = Qt.QLineEdit(str(self.delay_diff))
        self._delay_diff_tool_bar.addWidget(self._delay_diff_line_edit)
        self._delay_diff_line_edit.editingFinished.connect(
            lambda: self.set_delay_diff(int(str(self._delay_diff_line_edit.text()))))
        self.top_layout.addWidget(self._delay_diff_tool_bar)
        self._bandwidth_tool_bar = Qt.QToolBar(self)
        self._bandwidth_tool_bar.addWidget(Qt.QLabel("Signal Bandwidth (kHz)" + ": "))
        self._bandwidth_line_edit = Qt.QLineEdit(str(self.bandwidth))
        self._bandwidth_tool_bar.addWidget(self._bandwidth_line_edit)
        self._bandwidth_line_edit.editingFinished.connect(
            lambda: self.set_bandwidth(eng_notation.str_to_num(str(self._bandwidth_line_edit.text()))))
        self.top_layout.addWidget(self._bandwidth_tool_bar)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            5,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-50), (-30))
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(0.05)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['Antenna 1', 'Antenna 2', 'Interferometry', 'Antenna 3', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "yellow", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(5):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.pfb_arb_resampler_xxx_0 = pfb.arb_resampler_ccf(
            (samp_rate/(bandwidth*1e3)),
            taps=None,
            flt_size=32,
            atten=100)
        self.pfb_arb_resampler_xxx_0.declare_sample_delay(0)
        self.channels_channel_model_0_1_0 = channels.channel_model(
            noise_voltage=1.0,
            frequency_offset=(freq_diff_3 / samp_rate),
            epsilon=(1.0 + delay_rate_diff_3 * 1e-6),
            taps=[np.exp(1j * np.deg2rad(phase_diff_3))],
            noise_seed=4,
            block_tags=False)
        self.channels_channel_model_0_1 = channels.channel_model(
            noise_voltage=1.0,
            frequency_offset=(freq_diff_2 / samp_rate),
            epsilon=(1.0 + delay_rate_diff_2 * 1e-6),
            taps=[np.exp(1j * np.deg2rad(phase_diff_2))],
            noise_seed=3,
            block_tags=False)
        self.channels_channel_model_0_0 = channels.channel_model(
            noise_voltage=1.0,
            frequency_offset=0.0,
            epsilon=1.0,
            taps=[1.0],
            noise_seed=1,
            block_tags=False)
        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=1.0,
            frequency_offset=(freq_diff / samp_rate),
            epsilon=(1.0 + delay_rate_diff * 1e-6),
            taps=[np.exp(1j * np.deg2rad(phase_diff))],
            noise_seed=2,
            block_tags=False)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_delay_0_0_0 = blocks.delay(gr.sizeof_gr_complex*1, delay_diff_3)
        self.blocks_delay_0_0 = blocks.delay(gr.sizeof_gr_complex*1, delay_diff_2)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex*1, delay_diff)
        self.blocks_add_xx_1 = blocks.add_vcc(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, (frequency*1e3), 1, 0, 0)
        self.analog_noise_source_x_1 = analog.noise_source_c(analog.GR_GAUSSIAN, (np.sqrt(10**(snr/10.0)/(samp_rate/(bandwidth*1e3)))), 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_1, 0), (self.pfb_arb_resampler_xxx_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_add_xx_1, 0), (self.qtgui_freq_sink_x_0, 2))
        self.connect((self.blocks_delay_0, 0), (self.blocks_add_xx_1, 1))
        self.connect((self.blocks_delay_0, 0), (self.qtgui_freq_sink_x_0, 1))
        self.connect((self.blocks_delay_0_0, 0), (self.blocks_add_xx_1, 2))
        self.connect((self.blocks_delay_0_0, 0), (self.qtgui_freq_sink_x_0, 3))
        self.connect((self.blocks_delay_0_0_0, 0), (self.blocks_add_xx_1, 3))
        self.connect((self.blocks_delay_0_0_0, 0), (self.qtgui_freq_sink_x_0, 4))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.channels_channel_model_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.channels_channel_model_0_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.channels_channel_model_0_1, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.channels_channel_model_0_1_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.channels_channel_model_0_0, 0), (self.blocks_add_xx_1, 0))
        self.connect((self.channels_channel_model_0_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.channels_channel_model_0_1, 0), (self.blocks_delay_0_0, 0))
        self.connect((self.channels_channel_model_0_1_0, 0), (self.blocks_delay_0_0_0, 0))
        self.connect((self.pfb_arb_resampler_xxx_0, 0), (self.blocks_multiply_xx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "Interferometry")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_snr(self):
        return self.snr

    def set_snr(self, snr):
        self.snr = snr
        Qt.QMetaObject.invokeMethod(self._snr_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.snr)))
        self.analog_noise_source_x_1.set_amplitude((np.sqrt(10**(self.snr/10.0)/(self.samp_rate/(self.bandwidth*1e3)))))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_noise_source_x_1.set_amplitude((np.sqrt(10**(self.snr/10.0)/(self.samp_rate/(self.bandwidth*1e3)))))
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.channels_channel_model_0.set_frequency_offset((self.freq_diff / self.samp_rate))
        self.channels_channel_model_0_1.set_frequency_offset((self.freq_diff_2 / self.samp_rate))
        self.channels_channel_model_0_1_0.set_frequency_offset((self.freq_diff_3 / self.samp_rate))
        self.pfb_arb_resampler_xxx_0.set_rate((self.samp_rate/(self.bandwidth*1e3)))
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)

    def get_phase_diff_3(self):
        return self.phase_diff_3

    def set_phase_diff_3(self, phase_diff_3):
        self.phase_diff_3 = phase_diff_3
        Qt.QMetaObject.invokeMethod(self._phase_diff_3_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.phase_diff_3)))
        self.channels_channel_model_0_1_0.set_taps([np.exp(1j * np.deg2rad(self.phase_diff_3))])

    def get_phase_diff_2(self):
        return self.phase_diff_2

    def set_phase_diff_2(self, phase_diff_2):
        self.phase_diff_2 = phase_diff_2
        Qt.QMetaObject.invokeMethod(self._phase_diff_2_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.phase_diff_2)))
        self.channels_channel_model_0_1.set_taps([np.exp(1j * np.deg2rad(self.phase_diff_2))])

    def get_phase_diff(self):
        return self.phase_diff

    def set_phase_diff(self, phase_diff):
        self.phase_diff = phase_diff
        Qt.QMetaObject.invokeMethod(self._phase_diff_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.phase_diff)))
        self.channels_channel_model_0.set_taps([np.exp(1j * np.deg2rad(self.phase_diff))])

    def get_frequency(self):
        return self.frequency

    def set_frequency(self, frequency):
        self.frequency = frequency
        Qt.QMetaObject.invokeMethod(self._frequency_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.frequency)))
        self.analog_sig_source_x_0.set_frequency((self.frequency*1e3))

    def get_freq_diff_3(self):
        return self.freq_diff_3

    def set_freq_diff_3(self, freq_diff_3):
        self.freq_diff_3 = freq_diff_3
        Qt.QMetaObject.invokeMethod(self._freq_diff_3_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.freq_diff_3)))
        self.channels_channel_model_0_1_0.set_frequency_offset((self.freq_diff_3 / self.samp_rate))

    def get_freq_diff_2(self):
        return self.freq_diff_2

    def set_freq_diff_2(self, freq_diff_2):
        self.freq_diff_2 = freq_diff_2
        Qt.QMetaObject.invokeMethod(self._freq_diff_2_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.freq_diff_2)))
        self.channels_channel_model_0_1.set_frequency_offset((self.freq_diff_2 / self.samp_rate))

    def get_freq_diff(self):
        return self.freq_diff

    def set_freq_diff(self, freq_diff):
        self.freq_diff = freq_diff
        Qt.QMetaObject.invokeMethod(self._freq_diff_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.freq_diff)))
        self.channels_channel_model_0.set_frequency_offset((self.freq_diff / self.samp_rate))

    def get_delay_rate_diff_3(self):
        return self.delay_rate_diff_3

    def set_delay_rate_diff_3(self, delay_rate_diff_3):
        self.delay_rate_diff_3 = delay_rate_diff_3
        Qt.QMetaObject.invokeMethod(self._delay_rate_diff_3_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.delay_rate_diff_3)))
        self.channels_channel_model_0_1_0.set_timing_offset((1.0 + self.delay_rate_diff_3 * 1e-6))

    def get_delay_rate_diff_2(self):
        return self.delay_rate_diff_2

    def set_delay_rate_diff_2(self, delay_rate_diff_2):
        self.delay_rate_diff_2 = delay_rate_diff_2
        Qt.QMetaObject.invokeMethod(self._delay_rate_diff_2_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.delay_rate_diff_2)))
        self.channels_channel_model_0_1.set_timing_offset((1.0 + self.delay_rate_diff_2 * 1e-6))

    def get_delay_rate_diff(self):
        return self.delay_rate_diff

    def set_delay_rate_diff(self, delay_rate_diff):
        self.delay_rate_diff = delay_rate_diff
        Qt.QMetaObject.invokeMethod(self._delay_rate_diff_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.delay_rate_diff)))
        self.channels_channel_model_0.set_timing_offset((1.0 + self.delay_rate_diff * 1e-6))

    def get_delay_diff_3(self):
        return self.delay_diff_3

    def set_delay_diff_3(self, delay_diff_3):
        self.delay_diff_3 = delay_diff_3
        Qt.QMetaObject.invokeMethod(self._delay_diff_3_line_edit, "setText", Qt.Q_ARG("QString", str(self.delay_diff_3)))
        self.blocks_delay_0_0_0.set_dly(int(self.delay_diff_3))

    def get_delay_diff_2(self):
        return self.delay_diff_2

    def set_delay_diff_2(self, delay_diff_2):
        self.delay_diff_2 = delay_diff_2
        Qt.QMetaObject.invokeMethod(self._delay_diff_2_line_edit, "setText", Qt.Q_ARG("QString", str(self.delay_diff_2)))
        self.blocks_delay_0_0.set_dly(int(self.delay_diff_2))

    def get_delay_diff(self):
        return self.delay_diff

    def set_delay_diff(self, delay_diff):
        self.delay_diff = delay_diff
        Qt.QMetaObject.invokeMethod(self._delay_diff_line_edit, "setText", Qt.Q_ARG("QString", str(self.delay_diff)))
        self.blocks_delay_0.set_dly(int(self.delay_diff))

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        Qt.QMetaObject.invokeMethod(self._bandwidth_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.bandwidth)))
        self.analog_noise_source_x_1.set_amplitude((np.sqrt(10**(self.snr/10.0)/(self.samp_rate/(self.bandwidth*1e3)))))
        self.pfb_arb_resampler_xxx_0.set_rate((self.samp_rate/(self.bandwidth*1e3)))




def main(top_block_cls=Interferometry, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
