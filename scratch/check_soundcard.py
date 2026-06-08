import soundcard as sc

print("Speakers:")
for speaker in sc.all_speakers():
    print(f"- {speaker}")

print("\nMicrophones (including loopback):")
for mic in sc.all_microphones(include_loopback=True):
    print(f"- {mic}")

try:
    ds = sc.default_speaker()
    print(f"\nDefault Speaker: {ds}")
    print(f"Has recorder? {hasattr(ds, 'recorder')}")
    
    # Try to find a loopback for the default speaker
    mics = sc.all_microphones(include_loopback=True)
    loopback = next((m for m in mics if m.isloopback and ds.name in m.name), None)
    print(f"Found loopback for default speaker: {loopback}")
    
except Exception as e:
    print(f"Error: {e}")
