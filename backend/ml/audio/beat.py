import librosa

def beat_grid(wav_path):
    y, sr = librosa.load(wav_path, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
    return float(tempo), beats.tolist()
