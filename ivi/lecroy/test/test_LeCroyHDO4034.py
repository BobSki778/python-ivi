#!/usr/bin/env python
import ivi
print "Creating instrument object and connecting to instrument via USB..."
instr = ivi.lecroy.lecroyHDO4034('USB0::0x05FF::0x1023::INSTR')
#print "Creating instrument object and connecting to instrument via VXI11..."
#instr = ivi.lecroy.lecroyHDO4034('TCPIP::17.43.69.164::INSTR')
print 'Instrument Response to "*IDN?" query: {}'.format(instr._ask("*IDN?"))
print '\nDriver Info:'
print 'instr.identity.description = {}'.format(instr.identity.description)
print 'instr.identity.revision = {}'.format(instr.identity.revision)
print 'instr.identity.vendor = {}'.format(instr.identity.vendor)
print 'instr.identity.specification_major_version = {}'.format(instr.identity.specification_major_version)
print 'instr.identity.specification_minor_version = {}'.format(instr.identity.specification_minor_version)
print 'instr.identity.supported_instrument_models =\n{}'.format(instr.identity.supported_instrument_models)

print '\nDevice Instance Info:'
print 'instr.identity.instrument_manufacturer = {}'.format(instr.identity.instrument_manufacturer)
print 'instr.identity.instrument_model = {}'.format(instr.identity.instrument_model)
print 'instr.identity.instrument_firmware_revision = {}'.format(instr.identity.instrument_firmware_revision)
print 'instr.identity.instrument_serial_number = {}'.format(instr.identity.instrument_serial_number)
print 'instr.identity.instrument_serial_number = {}'.format(instr.identity.instrument_serial_number)

print '\nDevice Instance Analog Channel Info in lecroyBaseScope class:'
channel_names = instr._analog_channel_name # TODO: find if this is the "right" way to get this information from the driver
print 'instr._analog_channel_name list = {}'.format(channel_names)
for name in channel_names: print 'instr.channels[{name}].bw_limit = {value}'.format(name=name, value=instr.channels[name].bw_limit)
for name in channel_names: print 'instr.channels[{name}].invert = {value}'.format(name=name, value=instr.channels[name].invert)
for name in channel_names: print 'instr.channels[{name}].label = {value}'.format(name=name, value=instr.channels[name].label)
for name in channel_names: print 'instr.channels[{name}].label_position = {value}'.format(name=name, value=instr.channels[name].label_position)
for name in channel_names: print 'instr.channels[{name}].probe_skew = {value}'.format(name=name, value=instr.channels[name].probe_skew)
#for name in channel_names: print 'instr.channels[{name}].scale = {value}'.format(name=name, value=instr.channels[name].scale)
for name in channel_names: print 'instr.channels[{name}].trigger_level = {value}'.format(name=name, value=instr.channels[name].trigger_level)

print '\nDevice Instance Analog Channel Info in lecroyHDO class:'
for name in channel_names: print 'instr.channels[{name}].noise_filter = {value}'.format(name=name, value=instr.channels[name].noise_filter)
for name in channel_names: print 'instr.channels[{name}].interpolation = {value}'.format(name=name, value=instr.channels[name].interpolation)


