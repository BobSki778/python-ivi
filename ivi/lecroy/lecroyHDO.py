"""

Python Interchangeable Virtual Instrument Library

Copyright (c) 2012 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

# Commands for this scope series are referenced form the following documentation:
# http://cdn.teledynelecroy.com/files/manuals/wm-rcm-e_rev_d.pdf
# http://cdn.teledynelecroy.com/files/manuals/automation_command_ref_manual_ws.pdf
# http://cdn.teledynelecroy.com/files/manuals/automation_command_ref_manual_wr.pdf (used for lecroyWRXIA class upon which this code is based)

from .lecroyBaseScope import *


NoiseFilter = set(["None", "0.5bits", "1bits", "1.5bits", "2bits", "2.5bits", "3bits"])
ScreenshotImageFormatMapping = {
    'bmp': 'bmp',
    'bmp24': 'bmp',
    'bmp8': 'bmpcomp',
    'jpeg': 'jpeg',
    'png': 'png',
    'png24': 'png',
    'psd': 'psd',
    'tiff': 'tiff'}
TriggerTypes = set(['dropout', 'edge', 'glitch', 'interval', 'logic', 'qualified', 'runt', 'serial', 'slewrate', 'tv', 'width']) #eliminated 'slate' - what is that?
ExtTriggerSetting = set(["Ext", "ExtDivide10", "Line"])
VerticalCoupling = set(['ac', 'dc', 'gnd'])
BandwidthLimit = set(['Full', '20MHz', '200MHZ'])

class lecroyHDO(lecroyBaseScope):
    """LeCroy HDO series IVI oscilloscope driver"""

    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', '')

        super(lecroyHDO, self).__init__(*args, **kwargs)

        self._channel_interpolation = list()
        self._analog_channel_name = list()
        self._analog_channel_count = 4
        self._digital_channel_name = list()
        self._digital_channel_count = 16
        self._channel_count = self._analog_channel_count + self._digital_channel_count
        self._bandwidth = 1e9
        self._display_labels = True
        # self._channel_noise_filter = list()

        self._memory_size = 5

        self._identity_description = "LeCroy HDO series IVI oscilloscope driver"
        self._identity_supported_instrument_models = ['HDO4022',   'HDO4024',   'HDO4032',   'HDO4034',   'HDO4054',   'HDO4104',
                                                      'HDO4022-MS','HDO4024-MS','HDO4032-MS','HDO4034-MS','HDO4054-MS','HDO4104-MS']

        ivi.add_property(self, 'channels[].noise_filter',
                         self._get_channel_noise_filter,
                         self._set_channel_noise_filter,
                         None,
                         ivi.Doc("""
                        Specifies the channel enhanced noise filter bit setting. Set to 0 to turn off the filter.

                        Values:
                        * 0.0: 'None'
                        * 0.5: '0.5bits'
                        * 1.0: '1bits'
                        * 1.5: '1.5bits'
                        * 2.0: '2bits'
                        * 2.5: '2.5bits'
                        * 3.0: '3bits'
                        """))
        ivi.add_property(self, 'channels[].interpolation',
                         self._get_channel_interpolation,
                         self._set_channel_interpolation,
                         None,
                         ivi.Doc("""
                        Specifies the channel interpolation setting. Default is linear.

                        Values:
                        * Linear: Linear interpolation
                        * Sinxx: Sinx/x interpolation
                        """))

        self._init_channels()

    # Modified for LeCroy, WORKING ON HDO4034
    def _get_channel_label(self, index):
        """
        Get the label for the specified channel.
        """
        index = ivi.get_index(self._channel_name, index)
        if not self._driver_operation_simulate:
            self._channel_label[index] = self._ask("VBS? 'Return=app.Acquisition.{0}.LabelsText'".format(self._channel_name[index]))
        return self._channel_label[index]

    # Modified for LeCroy, WORKING ON HDO4034
    def _set_channel_label(self, index, value):
        """
        Set the label for the specified channel.
        """
        value = str(value)
        index = ivi.get_index(self._channel_name, index)
        if not self._driver_operation_simulate:
            self._write("VBS 'app.Acquisition.{0}.LabelsText = \"{1}\"'".format(self._channel_name[index], value))
            if self._display_labels == True:
                self._write("VBS 'app.Acquisition.{0}.ViewLabels = True'".format(self._channel_name[index]))
        self._channel_label[index] = value

    # Added for LeCroy, WORKING ON HDO4034
    def _get_channel_label_position(self, index):
        """
        Get the position of the label in seconds and Volts (or Amps or 
        whatever the vertical unit of the channel is).
        """
        index = ivi.get_index(self._channel_name, index)
        if not self._driver_operation_simulate:
#            self._channel_label_position[index] = float(self._ask('VBS? "Return=app.Acquisition.{0}.LabelsPosition"'.format(self._channel_name[index])).split('|')[0])
            self._channel_label_position[index] = self._ask("VBS? 'Return=app.Acquisition.{0}.LabelsPosition'".format(self._channel_name[index]))
        return self._channel_label_position[index]

    # Added for LeCroy, WORKING ON HDO4034
    def _set_channel_label_position(self, index, value):
        """
        Set the position of the label in seconds; data should be sent as a float
        ex: 55e-9 will result in a label position of 55 ns

        If display_labels is set to True then the new labels will be shown on the screen
        """
        value = str(value)
        index = ivi.get_index(self._channel_name, index)
        if not self._driver_operation_simulate:
            self._write("VBS 'app.Acquisition.{0}.LabelsPosition = \"{1}\"'".format(self._channel_name[index], value))
            if self._display_labels == True:
                self._write("VBS 'app.Acquisition.{0}.ViewLabels = True'".format(self._channel_name[index]))
        self._channel_label_position[index] = value

    # Modified for LeCroy, WORKING ON WR104XI-A
    def _get_channel_bw_limit(self, index):
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate:
            limits = (self._ask("VBS? 'Return=app.Acquisition.{0}.BandwidthLimit'".format(self._channel_name[index])))
            if self._channel_name[index] in limits:
                self._channel_bw_limit[index] = limits[limits.index(self._channel_name[index]) + 1]
        return self._channel_bw_limit[index]

    # Modified for LeCroy, WORKING ON WR104XI-A
    def _set_channel_bw_limit(self, index, value):
        """
        Sets the channel bandwidth limit setting:
        * 200MHz = 200 MHz bandwidth
        * 20MHz = 20 MHz bandwidth
        * Full = full bandwidth
        """
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate:
            self._write("VBS 'app.Acquisition.{0}.BandwidthLimit = \"{1}\"'".format(self._channel_name[index], value))
        self._channel_bw_limit[index] = value

    # Modified for LeCroy, WORKING ON WR104XI-A
    def _get_channel_invert(self, index):
        """
        Returns the status of the channel invert setting.
        * False = Not inverted
        * True = Inverted
        """
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate:
            self._channel_invert[index] = bool(
                int(self._ask("VBS? 'Return=app.Acquisition.{0}.Invert'".format(self._channel_name[index]))))
        return self._channel_invert[index]

    # Modified for LeCroy, WORKING ON WR104XI-A
    def _set_channel_invert(self, index, value):
        """
        Sets the channel invert setting:
        * False = Not inverted
        * True = Inverted
        """
        index = ivi.get_index(self._analog_channel_name, index)
        value = bool(value)
        if not self._driver_operation_simulate:
            self._write("VBS 'app.Acquisition.{0}.Invert = {1}'".format(self._channel_name[index], value))
        self._channel_invert[index] = value

    # Modified for LeCroy, WORKING ON WR104XI-A
    def _get_channel_noise_filter(self, index):
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate:
            self._channel_noise_filter[index] = self._ask("VBS? 'Return=app.Acquisition.{0}.EnhanceResType'".format(self._channel_name[index]))
        return self._channel_noise_filter[index]

    # Modified for LeCroy, WORKING ON WR104XI-A
    def _set_channel_noise_filter(self, index, filtertype):
        """
        Set the channel noise filter setting.

        Valid settings:
        * None
        * 0.5bits
        * 1bits
        * 1.5bits
        * 2bits
        * 2.5bits
        * 3bits
        """
        index = ivi.get_index(self._analog_channel_name, index)
        if filtertype not in NoiseFilter:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write("VBS 'app.Acquisition.{0}.EnhanceResType = \"{1}\"'".format(self._channel_name[index], filtertype))
        self._channel_noise_filter[index] = str(filtertype)

    # Modified for LeCroy, WORKING ON WR104XI-A
    def _get_channel_interpolation(self, index):
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate:
            self._channel_interpolation[index] = self._ask("VBS? 'Return=app.Acquisition.{0}.InterpolateType'".format(self._channel_name[index]))
        return self._channel_interpolation[index]

    # Modified for LeCroy, WORKING ON WR104XI-A
    def _set_channel_interpolation(self, index, interpolate_setting):
        """
        Set the channel interpolation setting.
        """
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate:
            self._write("VBS 'app.Acquisition.{0}.InterpolateType = \"{1}\"'".format(
                self._channel_name[index], interpolate_setting))
        self._channel_interpolation[index] = interpolate_setting

    # Modified for LeCroy, WORKING ON WR104XI-A
    def _get_channel_probe_skew(self, index):
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate:
            self._channel_probe_skew[index] = float(self._ask("VBS? 'Return=app.Acquisition.{0}.Deskew'".format(self._channel_name[index])))
        return self._channel_probe_skew[index]

    # Modified for LeCroy, WORKING ON WR104XI-A
    def _set_channel_probe_skew(self, index, value):
        index = ivi.get_index(self._analog_channel_name, index)
        value = float(value)
        if not self._driver_operation_simulate:
            self._write("VBS 'app.Acquisition.{0}.Deskew = \"{1:e}\"'".format(self._channel_name[index], value))
        self._channel_probe_skew[index] = value

    # Modified for LeCroy, WORKING ON WR104XI-A
    def _get_trigger_source(self):
        if not self._driver_operation_simulate:
            value = self._ask("VBS? 'Return=app.Acquisition.Trigger.Source'")
            self._trigger_source = value
        return self._trigger_source

    # Modified for LeCroy, WORKING ON WR104XI-A
    def _set_trigger_source(self, value):
        value = str(value)
        if (value not in self._channel_name) and (value not in ExtTriggerSetting):
            raise ivi.UnknownPhysicalNameException()
        if not self._driver_operation_simulate:
            self._write("VBS 'app.Acquisition.Trigger.Source = \"{0!s}\"'".format(value))
        self._trigger_source = value

    # Modified for LeCroy, WORKING ON WR104XI-A
    def _get_trigger_type(self):
        if not self._driver_operation_simulate:
            value = self._ask("VBS? 'Return=app.Acquisition.Trigger.Type'").lower()
            self._trigger_type = value
        return self._trigger_type

    # Modified for LeCroy, WORKING ON WR104XI-A
    def _set_trigger_type(self, value):
        value = value.lower()
        if value not in TriggerTypes:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write("VBS 'app.Acquisition.Trigger.Type = \"{0}\"'".format(value))
        self._trigger_type = value

    # Modified for LeCroy, WORKING ON WR104XI-A
    def _measurement_auto_setup(self):
        if not self._driver_operation_simulate:
            self._write("VBS 'app.AutoSetup'")

"""
    def _get_channel_scale(self, index):
        index = ivi.get_index(self._channel_name, index)
        if not self._driver_operation_simulate:
            self._channel_scale[index] = float(self._ask("{}:VDIV?".format(self._channel_name[index])))
            self._channel_range[index] = self._channel_scale[index] * self._vertical_divisions
        return self._channel_scale[index]

    def _set_channel_scale(self, index, value):
        index = ivi.get_index(self._channel_name, index)
        value = float(value)
        if not self._driver_operation_simulate:
            self._write("{}:VDIV {:e}".format((self._channel_name[index], value)))
        self._channel_scale[index] = value
        self._channel_range[index] = value * self._vertical_divisions
"""
