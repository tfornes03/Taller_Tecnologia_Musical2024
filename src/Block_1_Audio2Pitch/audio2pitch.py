import os
import sys
import csv
import matplotlib.pyplot as plt
import numpy as np
import librosa as li

from scipy.signal import get_window
sys.path.append('src/Block_1_Audio2Pitch/PSPM/')
import dftModel as DFT
import utilFunctions as UF
import harmonicModel as HM
import stft


################################################################
#HOW TO USE THIS CODE:
#Right after executing, write the name of the audio file you want to use.
#After that, enter 1, 2 or 3 in the terminal.
#1: For melodies with a fundemental frequency between 120 and 500 Hz.
#2: For human voice audios:
#### After selecting human voices, select the pitch of the audio:
#### 1: low frequencies (80-500 Hz)
#### 2: high frequencies (500-1000 Hz)
#3: For instruments audio:
#### 1: low frequencies (80-500 Hz)
#### 2: medium frequencies (500-1000 Hz)
#### 3: high frequencies (1000-10000 Hz)
#OUTPUT:
#The script displays the histogram of the sound with the fundemental frequency highlited in a black line.
#The fundemental frequency is also stored in a .cvs file.
################################################################

def get_user_input(prompt, valid_options):
    while True:
        try:
            selected = int(input(prompt))
            if selected in valid_options:
                return selected
            else:
                print(f"Invalid option. Please select one of the following: {valid_options}")
        except ValueError:
            print("Invalid input. Please enter a number.")

def audio2Pitch():

    audioName = input("Enter the name of the audio file: ")
    nameSplit = audioName.split(".")
    if nameSplit[-1] == 'wav':
        input_file = 'src/Block_1_Audio2Pitch/sounds/'+audioName
    else:
        input_file = 'src/Block_1_Audio2Pitch/sounds/'+audioName+'.wav'
        
    selected = get_user_input("Select input audio type, [1] normal, [2] high freq., [3] in progress: ", [1, 2, 3])

    if selected == 1:       #Normal option
        window, M, N, f0et, t, minf0, maxf0 = 'hamming', 8000, 8192, 10, -55, 120, 500
    elif selected == 2:     #High frequency option
        window, M, N, f0et, t = 'blackman', 8000, 8192, 10, -55
        selected = get_user_input("Select pitch range [1] for 80-500Hz, [2] for 500-1000Hz): ", [1, 2])
        if selected == 1:
            minf0 = 80
            maxf0 = 500
        elif selected == 2:
            minf0 = 500
            maxf0 = 1000
    elif selected == 3:     #Secondary option (still in prossess)
        window, M, N, f0et, t = 'hann', 16000, 16384, 10, -33
        selected = get_user_input("Select pitch range, [1] for 80-500Hz, [2] for 500-1000Hz, [3] for 1000-10000Hz): ", [1, 2, 3])
        if selected == 1:
            minf0 = 80
            maxf0 = 500
        elif selected == 2:
            minf0 = 500
            maxf0 = 1000
        elif selected == 3:
            minf0 = 1000
            maxf0 = 10000


    H = 256 
    x, fs = li.load(input_file)
    bpm, _ = li.beat.beat_track(y=x, sr=fs)


    w  = get_window(window, M)   
    f0 = HM.f0Detection(x, fs, w, N, H, t, minf0, maxf0, f0et) 

    maxplotfreq = 500.0    
    fig = plt.figure(figsize=(15, 9))

    mX, pX = stft.stftAnal(x, w, N, H) 
    mX = np.transpose(mX[:, :int(N * (maxplotfreq / fs)) + 1])
        
    timeStamps = np.arange(mX.shape[1]) * H / float(fs)                             
    binFreqs = np.arange(mX.shape[0]) * fs / float(N)
        
    output_dir = 'src/outputs/f0.csv'
    # Combine timestamps and f0 values into one array
    output_data = np.column_stack((timeStamps, f0))
    np.savetxt(output_dir, output_data, delimiter=',', fmt='%s')
    
    plt.pcolormesh(timeStamps, binFreqs, mX, shading='auto')
    plt.plot(timeStamps, f0, color = 'k', linewidth=1.5)
        
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (s)')
    plt.legend(('f0',))
    plt.show()

    return H, bpm, selected, output_data

    
