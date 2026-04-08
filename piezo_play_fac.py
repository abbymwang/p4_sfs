"""PLANTASIA
Author: Abby Wang
Date: April 7, 2026
Description: Python file for generating the notes registering vibrations from
the contact mics attached to the plant. Coded with the help of Claude.

Note, this requires installing the simpleaudio package: pip install pyserial simpleaudio numpy

To launch on the terminal: 
  python piezo_play_fac.py /dev/cu.usbmodem...
"""

import sys
import time
import threading
import numpy as np
import simpleaudio as sa
import serial
import serial.tools.list_ports

# ── Settings ──────────────────────────────────────────────────────────────────
SAMPLE_RATE = 44100
DURATION    = 0.6     # seconds
VOLUME      = 0.35    # per note (keep lower when playing chords)

NOTE_FREQS = {
    'F': 349.23,  # F4
    'A': 440.00,  # A4
    'C': 523.25,  # C5
}
# ──────────────────────────────────────────────────────────────────────────────


def find_arduino_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        desc = (p.description or "").lower()
        if any(kw in desc for kw in ("arduino", "ch340", "cp210", "ftdi", "usb serial")):
            return p.device
    if ports:
        return ports[0].device
    return None


def make_wave(freq):
    """Return a 16-bit PCM numpy array for a sine wave at freq Hz."""
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
    wave = VOLUME * np.sin(2 * np.pi * freq * t)
    # Fade out last 50ms to avoid clicking
    fade = int(SAMPLE_RATE * 0.05)
    wave[-fade:] *= np.linspace(1, 0, fade)
    # Convert to 16-bit PCM
    return (wave * 32767).astype(np.int16)


def play_note(freq):
    wave = make_wave(freq)
    play_obj = sa.play_buffer(wave, 1, 2, SAMPLE_RATE)
    play_obj.wait_done()


def play_notes_simultaneously(note_chars):
    threads = []
    for char in note_chars:
        freq = NOTE_FREQS.get(char)
        if freq:
            t = threading.Thread(target=play_note, args=(freq,))
            t.start()
            threads.append(t)
    for t in threads:
        t.join()


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else find_arduino_port()

    if not port:
        print("ERROR: No serial port found. Plug in your Arduino or pass the port as an argument.")
        sys.exit(1)

    print(f"Connecting to Arduino on {port} at 9600 baud…")

    try:
        with serial.Serial(port, 9600, timeout=1) as ser:
            time.sleep(2)
            ser.reset_input_buffer()
            print("Ready! Tap the piezos to play notes.")
            print("  A0 → F4 (349 Hz)")
            print("  A1 → A4 (440 Hz)")
            print("  A2 → C5 (523 Hz)")
            print("Press Ctrl+C to quit.\n")

            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    notes = [c for c in line if c in NOTE_FREQS]
                    if notes:
                        label = " + ".join(
                            f"{c}({'F4' if c=='F' else 'A4' if c=='A' else 'C5'})"
                            for c in notes
                        )
                        print(f"  ♪ {label}")
                        threading.Thread(
                            target=play_notes_simultaneously,
                            args=(notes,),
                            daemon=True
                        ).start()

    except serial.SerialException as e:
        print(f"Serial error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nDone.")


if __name__ == "__main__":
    main()