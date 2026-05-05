"""
sound_manager.py - Sound Effects Manager
=========================================
Handles loading and playing sound effects with graceful
fallback when audio files are missing or audio is unavailable.
"""

import pygame
import os


class SoundManager:
    """
    Manages game sound effects and background music.
    
    Attempts to load sounds from the assets/ directory.
    If files are missing or audio is unavailable, the game
    continues silently without errors.
    
    Expected sound files in assets/:
        - pickup.wav   : Key collection sound
        - hit.wav      : Player takes damage
        - win.wav      : Victory sound
        - lose.wav     : Game over sound
        - door.wav     : Door opening sound
    """

    def __init__(self, assets_dir="assets"):
        """
        Initialize the sound manager.
        
        Args:
            assets_dir : Path to the assets folder
        """
        self.enabled = False
        self.sounds = {}
        self.assets_dir = assets_dir

        # Try to initialize the mixer
        try:
            pygame.mixer.init()
            self.enabled = True
            self._load_sounds()
        except Exception as e:
            print(f"[SoundManager] Audio unavailable: {e}")
            print("[SoundManager] Game will run without sound.")

    def _load_sounds(self):
        """
        Attempt to load sound files from the assets directory.
        Missing files are logged but do not cause errors.
        """
        sound_files = {
            "pickup": "pickup.wav",
            "hit": "hit.wav",
            "win": "win.wav",
            "lose": "lose.wav",
            "door": "door.wav",
        }

        for name, filename in sound_files.items():
            filepath = os.path.join(self.assets_dir, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                    print(f"[SoundManager] Loaded: {filename}")
                except Exception as e:
                    print(f"[SoundManager] Failed to load {filename}: {e}")
            # If file doesn't exist, we simply skip it (no error)

    def play(self, sound_name):
        """
        Play a sound effect by name.
        Silently does nothing if the sound is not loaded.
        
        Args:
            sound_name : Key name of the sound (e.g., "pickup", "hit")
        """
        if not self.enabled:
            return
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass  # Silently ignore playback errors

    def play_music(self, filepath, loops=-1, volume=0.3):
        """
        Play background music from a file.
        
        Args:
            filepath : Path to the music file
            loops    : Number of loops (-1 for infinite)
            volume   : Volume level (0.0 to 1.0)
        """
        if not self.enabled:
            return
        if os.path.exists(filepath):
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loops)
            except Exception as e:
                print(f"[SoundManager] Music error: {e}")

    def stop_music(self):
        """Stop any currently playing background music."""
        if self.enabled:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
