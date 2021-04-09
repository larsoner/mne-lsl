from __future__ import print_function, division, unicode_literals

"""
Export Matlab signal data into fif format.
"""
import scipy.io
import numpy as np
import neurodecode.utils.q_common as qc
from neurodecode import logger
import mne

#----------------------------------------------------------------------
def mat2fif(mat_file, sample_rate, data_field, event_field):
    """
    Convert a mat file to MNE format (.fif)
    
    mat_file : str
        The path to the matlab file to convert
    sample_rate: float
        The sampling rate [Hz]
    data_field : str
        Signal field name in mat structure
    event_field : str
        Events field name in mat structure
    """
    # Load from matfile
    data = scipy.io.loadmat(mat_file)
    
    # Extract info
    eeg_data = data[data_field]
    event_data = data[event_field]
    assert event_data.shape[1] == eeg_data.shape[1]

    num_eeg_channels = eeg_data.shape[0]    
    ch_names = ['TRIGGER'] + ['CH%d' % ch for ch in range(num_eeg_channels)]
    ch_info = ['stim'] + ['eeg'] * num_eeg_channels

    signals = np.concatenate( (event_data, eeg_data), axis=0 )
    
    # Create MNE structure 
    info = mne.create_info(ch_names, sample_rate, ch_info)
    raw = mne.io.RawArray(signals, info)

    # Save
    [basedir, fname, fext] = qc.parse_path_list(mat_file)
    fifname = '%s/%s.fif' % (basedir, fname)
    raw.save(fifname, verbose=False, overwrite=True)
    logger.info('Saved to %s.' % fifname)

#----------------------------------------------------------------------
if __name__ == '__main__':
    mat_file = r'D:\data\Phoneme\data.mat'
    sample_rate = 1000.0
    data_field = 'ecog' # data containing signals
    event_field = 'phoneme' # data containing events
    
    if len(sys.argv) > 2:
        raise IOError("Two many arguments provided, max is 4 (matfile, sample_rate, data_field, event_field)")
    
    elif len(sys.argv) > 3:
        data_field = sys.argv[3]
        event_field = input('Event field name: \n>> ')    
    
    elif len(sys.argv) > 2:
        sample_rate = sys.argv[2]
        data_field = input('Data field name: \n>> ')

    elif len(sys.argv) > 1:
        mat_file = sys.argv[1]
        sample_rate = float(input('Sampling rate: \n>> '))
    
    elif len(sys.argv) == 1:
        mat_file = input('Provide the mat file path: \n>> ')    
    
    mat2fif(mat_file, sample_rate, data_field, event_field)