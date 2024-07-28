Method 1:
- My method. With lower and upper threshold
- Extract locations, pull them out, then itll get transformed in the forward function
* Pros:
    - Did the work for it already
    - Used in all of the recorded data right now
* Cons:
    - wasnt the vetted method
    - Thresholds may differ per person, requires MUCH more time processing

Method 2:
- Use keystroke code to extract data to tensors, then that goes directly to the model
* Pros:
    - Automated, vetted method
* Cons:
    - I didnt do any work on this end. Didnt see it earlier
    - Requires rewrite of my modal.

```python
def isolator(signal, sample_rate, size, scan, before, after, threshold, show=False):
    strokes = []
    # -- signal'
    if show:
        plt.figure(figsize=(7, 2))
        librosa.display.waveshow(signal, sr=sample_rate)
    fft = librosa.stft(signal, n_fft=size, hop_length=scan)
    energy = np.abs(np.sum(fft, axis=0)).astype(float)
    # norm = np.linalg.norm(energy)
    # energy = energy/norm
    # -- energy'
    if show:
        plt.figure(figsize=(7, 2))
        librosa.display.waveshow(energy)
    threshed = energy > threshold
    # -- peaks'
    if show:
        plt.figure(figsize=(7, 2))
        librosa.display.waveshow(threshed.astype(float))
    peaks = np.where(threshed == True)[0]
    peak_count = len(peaks)
    prev_end = sample_rate*0.1*(-1)
    # '-- isolating keystrokes'
    for i in range(peak_count):
        this_peak = peaks[i]
        timestamp = (this_peak*scan) + size//2
        if timestamp > prev_end + (0.1*sample_rate):
            keystroke = signal[timestamp-before:timestamp+after]
            strokes.append(torch.tensor(keystroke)[None, :])
            if show:
                plt.figure(figsize=(7, 2))
                librosa.display.waveshow(keystroke, sr=sample_rate)
            prev_end = timestamp+after
    return strokes


AUDIO_FILE = '../data/research/MBPWavs/key_data/'
keys_s = '1234567890qwertyuiopasdfghjklzxcvbnm'
labels = list(keys_s)
keys = ['key_press_' + k + '_label.wav' for k in labels]
data_dict = {'Key':[], 'File':[]}

for i, File in enumerate(keys):
    loc = AUDIO_FILE + File
    samples, sample_rate = librosa.load(loc, sr=None)
    #samples = samples[round(1*sample_rate):]
    strokes = []
    prom = 0.06
    step = 0.005
    while not len(strokes) == 25:
        strokes = isolator(samples[1*sample_rate:], sample_rate, 48, 24, 2400, 12000, prom, False)
        if len(strokes) < 25:
            prom -= step
        if len(strokes) > 25:
            prom += step
        if prom <= 0:
            print('-- not possible for: ',File)
            break
        step = step*0.99
    label = [labels[i]]*len(strokes)
    data_dict['Key'] += label
    data_dict['File'] += strokes

df = pd.DataFrame(data_dict)
mapper = {}
counter = 0
for l in df['Key']:
    if not l in mapper:
        mapper[l] = counter
        counter += 1
df.replace({'Key': mapper}, inplace=True)
```