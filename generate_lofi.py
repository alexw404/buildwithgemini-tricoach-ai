import numpy as np
from scipy.io import wavfile
import random

def create_upbeat_lofi(duration_sec=30, sample_rate=44100):
    total_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, total_samples, endpoint=False)
    
    # 88 BPM -> beat = 60 / 88 = 0.6818 sec, bar = 2.727 sec
    bpm = 88.0
    beat_dur = 60.0 / bpm
    bar_dur = beat_dur * 4
    
    # Initialize stereo channels
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)
    
    # 1. Warm Rhodes / Electric Piano Chords
    # Fmaj7, Em7, Dm7, Cmaj7
    chords = [
        [174.61, 220.00, 261.63, 329.63], # Fmaj7 (F3, A3, C4, E4)
        [164.81, 196.00, 246.94, 293.66], # Em7   (E3, G3, B3, D4)
        [146.83, 174.61, 220.00, 261.63], # Dm7   (D3, F3, A3, C4)
        [130.81, 164.81, 196.00, 246.94], # Cmaj7 (C3, E3, G3, B3)
    ]
    
    num_bars = int(np.ceil(duration_sec / bar_dur))
    
    for b in range(num_bars):
        bar_start_time = b * bar_dur
        chord = chords[b % len(chords)]
        
        # Play chord twice per bar (strummed on beat 1 and beat 2.5)
        strum_times = [bar_start_time, bar_start_time + 2.5 * beat_dur]
        for st in strum_times:
            if st >= duration_sec:
                continue
            start_idx = int(st * sample_rate)
            chord_len = int(2.2 * beat_dur * sample_rate)
            end_idx = min(start_idx + chord_len, total_samples)
            actual_len = end_idx - start_idx
            
            if actual_len <= 0:
                continue
                
            t_env = np.linspace(0, actual_len / sample_rate, actual_len)
            # Smooth exponential attack and decay
            env = np.exp(-1.8 * t_env) * (1.0 - np.exp(-30.0 * t_env))
            
            chord_signal_l = np.zeros(actual_len, dtype=np.float32)
            chord_signal_r = np.zeros(actual_len, dtype=np.float32)
            
            for idx, freq in enumerate(chord):
                # Add fundamental + warm 2nd/3rd harmonics + subtle vibrato
                vib = np.sin(2 * np.pi * 5.0 * t_env) * 0.8
                note = (
                    0.6 * np.sin(2 * np.pi * (freq + vib) * t_env) +
                    0.25 * np.sin(2 * np.pi * (freq * 2.0) * t_env) +
                    0.1 * np.sin(2 * np.pi * (freq * 3.0) * t_env)
                )
                pan = 0.4 + 0.05 * idx # Stereo spread
                chord_signal_l += note * env * (1.0 - pan)
                chord_signal_r += note * env * pan
                
            left[start_idx:end_idx] += chord_signal_l * 0.35
            right[start_idx:end_idx] += chord_signal_r * 0.35

    # 2. Smooth Sub Bass Line
    bass_freqs = [87.31, 82.41, 73.42, 65.41] # F2, E2, D2, C2
    for b in range(num_bars):
        bar_start_time = b * bar_dur
        freq = bass_freqs[b % len(bass_freqs)]
        
        # Bass pattern: beat 1, beat 2.5, beat 3.5
        bass_beats = [0.0, 1.5, 2.5, 3.5]
        for bb in bass_beats:
            bt = bar_start_time + bb * beat_dur
            if bt >= duration_sec:
                continue
            start_idx = int(bt * sample_rate)
            bass_len = int(0.9 * beat_dur * sample_rate)
            end_idx = min(start_idx + bass_len, total_samples)
            actual_len = end_idx - start_idx
            if actual_len <= 0:
                continue
            t_b = np.linspace(0, actual_len / sample_rate, actual_len)
            b_env = np.exp(-3.0 * t_b) * (1.0 - np.exp(-40.0 * t_b))
            # Deep low-passed sine wave
            b_sig = 0.8 * np.sin(2 * np.pi * freq * t_b) + 0.2 * np.sin(2 * np.pi * (freq * 2) * t_b)
            left[start_idx:end_idx] += b_sig * b_env * 0.4
            right[start_idx:end_idx] += b_sig * b_env * 0.4

    # 3. Upbeat Lo-Fi Drum Loop (Kick, Snare, Hi-Hat)
    num_beats = int(duration_sec / beat_dur)
    for beat in range(num_beats):
        bt = beat * beat_dur
        
        # Kick on beat 1 and beat 3 (and 2.75 syncopation)
        kick_beats = [0.0, 2.0, 2.75]
        for kb in kick_beats:
            kt = (beat // 4 * 4 + (beat % 4)) * beat_dur
            if beat % 4 == 0 and kb == 0.0 or beat % 4 == 2 and kb == 2.0 or beat % 4 == 2 and kb == 2.75:
                start_idx = int((bt + (kb if beat % 4 == 2 and kb == 2.75 else 0)) * sample_rate)
                k_len = int(0.18 * sample_rate)
                end_idx = min(start_idx + k_len, total_samples)
                actual_len = end_idx - start_idx
                if actual_len > 0:
                    t_k = np.linspace(0, actual_len / sample_rate, actual_len)
                    # Pitch sweep kick
                    k_freq = 120.0 * np.exp(-30.0 * t_k) + 45.0
                    k_env = np.exp(-12.0 * t_k)
                    k_sig = np.sin(2 * np.pi * k_freq * t_k) * k_env * 0.6
                    left[start_idx:end_idx] += k_sig
                    right[start_idx:end_idx] += k_sig

        # Snare/Rim on beat 2 and beat 4
        if beat % 2 == 1:
            start_idx = int(bt * sample_rate)
            s_len = int(0.15 * sample_rate)
            end_idx = min(start_idx + s_len, total_samples)
            actual_len = end_idx - start_idx
            if actual_len > 0:
                t_s = np.linspace(0, actual_len / sample_rate, actual_len)
                s_env = np.exp(-22.0 * t_s)
                s_noise = np.random.normal(0, 0.4, actual_len) * s_env
                s_tone = np.sin(2 * np.pi * 180 * t_s) * s_env * 0.3
                s_sig = (s_noise + s_tone) * 0.35
                left[start_idx:end_idx] += s_sig
                right[start_idx:end_idx] += s_sig

        # Hi-Hats on 8th notes (0.0 and 0.5) with lo-fi swing
        for hat in [0.0, 0.5]:
            hat_t = bt + hat * beat_dur
            if hat == 0.5:
                hat_t += 0.02 # Slight swing
            if hat_t < duration_sec:
                start_idx = int(hat_t * sample_rate)
                h_len = int(0.05 * sample_rate)
                end_idx = min(start_idx + h_len, total_samples)
                actual_len = end_idx - start_idx
                if actual_len > 0:
                    t_h = np.linspace(0, actual_len / sample_rate, actual_len)
                    h_env = np.exp(-60.0 * t_h)
                    h_sig = np.random.normal(0, 0.25, actual_len) * h_env * (0.25 if hat == 0.0 else 0.18)
                    left[start_idx:end_idx] += h_sig * 0.8
                    right[start_idx:end_idx] += h_sig * 1.2

    # 4. Subtle Lo-Fi Vinyl Crackle / Warmth
    crackle = np.random.normal(0, 0.015, total_samples)
    # Low-pass filter crackle for warmth
    left += crackle
    right += crackle
    
    # Normalize mix to prevent clipping
    max_val = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if max_val > 0:
        left = (left / max_val) * 0.85
        right = (right / max_val) * 0.85

    # Convert to 16-bit PCM WAV
    audio_stereo = np.vstack((left, right)).T
    audio_int16 = (audio_stereo * 32767).astype(np.int16)
    
    output_path = "lofi_music.wav"
    wavfile.write(output_path, sample_rate, audio_int16)
    print(f"Upbeat lo-fi track generated: {output_path}")
    return output_path

if __name__ == "__main__":
    create_upbeat_lofi(duration_sec=35)
