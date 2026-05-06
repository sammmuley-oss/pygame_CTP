"""
sound_manager.py - Sound Effects Manager
=========================================
Generates all game sounds synthetically (no external files needed).
Unified kill sound across all maps.  Ambient Nether atmosphere
(lava bubbles, eerie wind, crackling fire) during gameplay.
No player footstep sounds.
"""

import pygame
import numpy as np
import os
import math


# ── Synthesis helpers ──────────────────────────────────────────────

SAMPLE_RATE = 44100

def _make_sound(samples_float):
    """Convert a float64 mono array (±1.0) → stereo pygame.mixer.Sound."""
    samples_float = np.clip(samples_float, -1.0, 1.0)
    int_samples = (samples_float * 32767).astype(np.int16)
    stereo = np.column_stack((int_samples, int_samples))
    return pygame.sndarray.make_sound(stereo)


def _fade_env(n, attack=0.01, release=0.05, sr=SAMPLE_RATE):
    """Smooth attack/release envelope (avoids clicks)."""
    env = np.ones(n, dtype=np.float64)
    att = int(attack * sr)
    rel = int(release * sr)
    if att > 0 and att < n:
        env[:att] = np.linspace(0, 1, att)
    if rel > 0 and rel < n:
        env[-rel:] = np.linspace(1, 0, rel)
    return env


def _simple_reverb(sig, sr=SAMPLE_RATE, delay_ms=45, decay=0.30, taps=4):
    """Add a subtle multi-tap reverb/echo to simulate open Nether space."""
    out = sig.copy()
    for i in range(1, taps + 1):
        d = int(delay_ms * i * sr / 1000)
        gain = decay ** i
        if d < len(sig):
            out[d:] += sig[:-d] * gain
    peak = np.max(np.abs(out))
    if peak > 0.95:
        out *= 0.95 / peak
    return out


# ── Sound generators ─────────────────────────────────────────────


def _gen_kill():
    """Unified kill sound — sharp blade impact with a satisfying punch.
    Used across ALL map themes.
    """
    dur = 0.35
    n = int(dur * SAMPLE_RATE)
    t = np.linspace(0, dur, n, dtype=np.float64)

    freq = 200 + 350 * (t / dur) ** 0.5
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    sig = 0.55 * np.sin(phase)
    sig += 0.25 * np.sin(phase * 2.02)
    impact_start = int(0.2 * SAMPLE_RATE)
    impact_env = np.zeros(n)
    imp_len = n - impact_start
    if imp_len > 0:
        impact_env[impact_start:] = np.exp(-np.linspace(0, 10, imp_len))
    sig += 0.40 * np.sin(2 * np.pi * 75 * t) * impact_env
    hit_env = np.zeros(n)
    hit_len = min(int(0.06 * SAMPLE_RATE), n - impact_start)
    if hit_len > 0:
        hit_env[impact_start:impact_start + hit_len] = np.exp(
            -np.linspace(0, 12, hit_len))
    sig += 0.20 * np.random.randn(n) * hit_env

    sig *= _fade_env(n, attack=0.005, release=0.06)
    return _make_sound(sig)


def _gen_bot_move():
    """Guard patrol movement sound — muffled step."""
    dur = 0.14
    n = int(dur * SAMPLE_RATE)
    t = np.linspace(0, dur, n, dtype=np.float64)

    sig = 0.25 * np.sin(2 * np.pi * 65 * t) * np.exp(-t * 22)
    noise = np.random.randn(n)
    kernel = np.ones(18) / 18
    sig += 0.15 * np.convolve(noise, kernel, mode='same') * np.exp(-t * 28)
    sig += 0.08 * np.sin(2 * np.pi * 120 * t) * np.exp(-t * 35)
    sig *= _fade_env(n, attack=0.002, release=0.02)
    sig = _simple_reverb(sig, delay_ms=30, decay=0.18, taps=2)
    return _make_sound(sig)


def _gen_block_bump():
    """Wall collision — Minecraft-style bush/leaf scrape rustle."""
    dur = 0.18
    n = int(dur * SAMPLE_RATE)
    t = np.linspace(0, dur, n, dtype=np.float64)

    # Layer 1: broad leafy rustle (low-pass filtered noise)
    noise1 = np.random.randn(n)
    kernel1 = np.ones(12) / 12
    rustle = np.convolve(noise1, kernel1, mode='same')
    sig = 0.50 * rustle * np.exp(-t * 14)

    # Layer 2: higher scrape texture (lighter filter)
    noise2 = np.random.randn(n)
    kernel2 = np.ones(5) / 5
    scrape = np.convolve(noise2, kernel2, mode='same')
    sig += 0.25 * scrape * np.exp(-t * 20)

    # Layer 3: faint leafy swish tone
    sig += 0.10 * np.sin(2 * np.pi * 220 * t) * np.exp(-t * 30)
    sig += 0.06 * np.sin(2 * np.pi * 350 * t) * np.exp(-t * 40)

    sig *= _fade_env(n, attack=0.003, release=0.04)
    return _make_sound(sig)


def _gen_lose():
    """Game over / detected sound."""
    dur = 0.6
    n = int(dur * SAMPLE_RATE)
    t = np.linspace(0, dur, n, dtype=np.float64)

    freq = 400 - 250 * (t / dur)
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    sig = 0.55 * np.sin(phase) * np.exp(-t * 3)
    sig += 0.25 * np.sin(phase * 0.5) * np.exp(-t * 4)
    sig *= _fade_env(n, attack=0.005, release=0.10)
    return _make_sound(sig)


def _gen_win():
    """Level clear / victory arpeggio."""
    dur = 0.7
    n = int(dur * SAMPLE_RATE)
    t = np.linspace(0, dur, n, dtype=np.float64)

    sig = np.zeros(n, dtype=np.float64)
    notes = [523, 659, 784]
    note_dur = dur / 3
    for i, freq in enumerate(notes):
        start = int(i * note_dur * SAMPLE_RATE)
        end = min(int((i + 1) * note_dur * SAMPLE_RATE), n)
        ln = end - start
        tn = np.linspace(0, note_dur, ln)
        note = 0.50 * np.sin(2 * np.pi * freq * tn) * np.exp(-tn * 3)
        note += 0.15 * np.sin(2 * np.pi * freq * 2 * tn) * np.exp(-tn * 5)
        sig[start:end] += note

    sig *= _fade_env(n, attack=0.005, release=0.08)
    return _make_sound(sig)


# ── Ambient Nether generators ────────────────────────────────────

def _gen_ambient_lava_bubble():
    """Distant lava bubbling — random low pops and gurgles."""
    dur = 2.5
    n = int(dur * SAMPLE_RATE)
    t = np.linspace(0, dur, n, dtype=np.float64)
    sig = np.zeros(n, dtype=np.float64)

    np.random.seed(42)
    for _ in range(6):
        offset = np.random.uniform(0.1, dur - 0.3)
        bubble_dur = np.random.uniform(0.08, 0.18)
        freq = np.random.uniform(55, 95)
        start = int(offset * SAMPLE_RATE)
        blen = int(bubble_dur * SAMPLE_RATE)
        end = min(start + blen, n)
        blen = end - start
        if blen <= 0:
            continue
        bt = np.linspace(0, bubble_dur, blen)
        bfreq = freq + 30 * np.sin(np.pi * bt / bubble_dur)
        bphase = 2 * np.pi * np.cumsum(bfreq) / SAMPLE_RATE
        bubble = 0.30 * np.sin(bphase) * np.exp(-bt * 8)
        bubble += 0.08 * np.random.randn(blen) * np.exp(-bt * 12)
        sig[start:end] += bubble

    np.random.seed(None)
    sig *= _fade_env(n, attack=0.05, release=0.15)
    sig = _simple_reverb(sig, delay_ms=60, decay=0.25, taps=3)
    return _make_sound(sig)


def _gen_ambient_wind():
    """Low eerie Nether wind — slow filtered noise drone."""
    dur = 3.0
    n = int(dur * SAMPLE_RATE)
    t = np.linspace(0, dur, n, dtype=np.float64)

    noise = np.random.randn(n)
    kernel = np.ones(80) / 80
    wind = np.convolve(noise, kernel, mode='same')
    mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * t)
    sig = 0.35 * wind * mod
    sig += 0.10 * np.sin(2 * np.pi * 32 * t) * mod
    sig += 0.06 * np.sin(2 * np.pi * 48 * t + 0.3) * mod

    sig *= _fade_env(n, attack=0.20, release=0.30)
    return _make_sound(sig)


def _gen_ambient_fire_crackle():
    """Faint crackling fire — random snaps and pops."""
    dur = 2.0
    n = int(dur * SAMPLE_RATE)
    t = np.linspace(0, dur, n, dtype=np.float64)
    sig = np.zeros(n, dtype=np.float64)

    np.random.seed(77)
    for _ in range(10):
        offset = np.random.uniform(0.05, dur - 0.1)
        snap_dur = np.random.uniform(0.01, 0.04)
        start = int(offset * SAMPLE_RATE)
        slen = int(snap_dur * SAMPLE_RATE)
        end = min(start + slen, n)
        slen = end - start
        if slen <= 0:
            continue
        st = np.linspace(0, snap_dur, slen)
        snap = 0.35 * np.random.randn(slen) * np.exp(-st * 80)
        snap += 0.15 * np.sin(2 * np.pi * 800 * st) * np.exp(-st * 100)
        sig[start:end] += snap

    np.random.seed(None)

    hiss = np.random.randn(n)
    hiss_kernel = np.ones(10) / 10
    hiss_filtered = np.convolve(hiss, hiss_kernel, mode='same')
    sig += 0.06 * hiss_filtered

    sig *= _fade_env(n, attack=0.05, release=0.10)
    sig = _simple_reverb(sig, delay_ms=40, decay=0.15, taps=2)
    return _make_sound(sig)


# ── SoundManager class ────────────────────────────────────────────

class SoundManager:
    """
    Manages all game audio.  Unified kill sound across all maps.
    No player footstep sounds.  Ambient Nether atmosphere during gameplay.
    """

    _COOLDOWNS = {}

    def __init__(self, assets_dir="assets"):
        self.enabled = False
        self.sounds = {}
        self.assets_dir = assets_dir
        self._cooldown_counters = {}
        self._music_playing = False
        self._bgm_file = None

        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=1024)
            pygame.mixer.set_num_channels(24)
            self.enabled = True
            self._generate_sounds()
        except Exception as e:
            print(f"[SoundManager] Audio unavailable: {e}")
            print("[SoundManager] Game will run without sound.")

    def _generate_sounds(self):
        """Generate all synthetic sounds."""
        print("[SoundManager] Generating sounds…")

        # General events (win / lose only)
        self.sounds["lose"] = _gen_lose()
        self.sounds["win"] = _gen_win()

        # Kill sound — Among Us external audio file
        self._kill_sfx_file = None
        kill_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "among us final clip.mp3")
        if os.path.exists(kill_path):
            self._kill_sfx_file = kill_path
            try:
                self._kill_sound = pygame.mixer.Sound(kill_path)
                self._kill_sound.set_volume(0.85)
                self.sounds["kill"] = self._kill_sound
                print(f"[SoundManager] Kill SFX found: {os.path.basename(kill_path)}")
            except Exception as e:
                print(f"[SoundManager] Kill SFX load error: {e}")
                self.sounds["kill"] = _gen_kill()
        else:
            print("[SoundManager] Among Us clip not found, using synthetic kill sound.")
            self.sounds["kill"] = _gen_kill()

        # Background music — load external audio file
        self._bgm_file = None
        bgm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "WhatsApp Audio 2026-05-06 at 8.59.11 PM.mpeg")
        if os.path.exists(bgm_path):
            self._bgm_file = bgm_path
            print(f"[SoundManager] BGM file found: {os.path.basename(bgm_path)}")
        else:
            print("[SoundManager] BGM file not found, lobby will have no music.")

        # Launch screen SFX — nether portal audio
        self._launch_sfx_file = None
        launch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "nether_portal.mp3")
        if os.path.exists(launch_path):
            self._launch_sfx_file = launch_path
            print(f"[SoundManager] Launch SFX found: {os.path.basename(launch_path)}")
        else:
            print("[SoundManager] nether_portal.mp3 not found, launch will be silent.")

        # ── Volume calibration ──
        self.sounds["kill"].set_volume(0.85)
        self.sounds["lose"].set_volume(0.65)
        self.sounds["win"].set_volume(0.70)

        print("[SoundManager] All sounds ready.")

    # ── Playback ─────────────────────────────────────────────────

    def play(self, sound_name):
        """Play a sound effect by name (with optional cooldown)."""
        if not self.enabled:
            return
        cd = self._COOLDOWNS.get(sound_name, 0)
        if cd > 0:
            counter = self._cooldown_counters.get(sound_name, 0)
            if counter > 0:
                return
            self._cooldown_counters[sound_name] = cd

        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass

    def play_kill(self, theme_style=None):
        """Play the Among Us kill sound."""
        self.play("kill")

    def play_block_touch(self, theme_style=None):
        """Silent — block collision sound disabled."""
        pass

    def tick_cooldowns(self):
        """Call once per frame to decrement cooldown counters."""
        for key in list(self._cooldown_counters):
            if self._cooldown_counters[key] > 0:
                self._cooldown_counters[key] -= 1

    def tick_ambient(self):
        """Ambient sounds disabled — no in-game atmosphere."""
        pass

    # ── Background music ─────────────────────────────────────────

    def start_menu_music(self):
        """Start looping lobby BGM using pygame.mixer.music."""
        if not self.enabled or self._music_playing:
            return
        if not self._bgm_file:
            return
        try:
            pygame.mixer.music.load(self._bgm_file)
            pygame.mixer.music.set_volume(0.75)
            pygame.mixer.music.play(loops=-1)
            self._music_playing = True
        except Exception as e:
            print(f"[SoundManager] BGM playback error: {e}")

    def stop_menu_music(self):
        """Stop lobby BGM."""
        if not self.enabled or not self._music_playing:
            return
        try:
            pygame.mixer.music.fadeout(500)
            self._music_playing = False
        except Exception:
            pass

    @property
    def is_music_playing(self):
        return self._music_playing

    # ── Launch screen SFX ────────────────────────────────────────

    def play_launch_sfx(self):
        """Play the nether portal audio during the launching screen."""
        if not self.enabled:
            return
        if not self._launch_sfx_file:
            return
        try:
            pygame.mixer.music.load(self._launch_sfx_file)
            pygame.mixer.music.set_volume(0.85)
            pygame.mixer.music.play(loops=0)
            self._music_playing = False
        except Exception as e:
            print(f"[SoundManager] Launch SFX error: {e}")

    def stop_launch_sfx(self):
        """Stop the nether portal audio."""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.fadeout(400)
        except Exception:
            pass

    # Legacy wrappers
    def play_music(self, filepath, loops=-1, volume=0.3):
        pass

    def stop_music(self):
        self.stop_menu_music()
