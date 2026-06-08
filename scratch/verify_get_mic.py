import soundcard as sc

try:
    ds = sc.default_speaker()
    print(f"Default Speaker: {ds.name}")
    
    # Try getting the microphone by name with loopback
    mic = sc.get_microphone(id=ds.name, include_loopback=True)
    print(f"Obtained Mic: {mic}")
    print(f"Is Loopback? {mic.isloopback}")
    
except Exception as e:
    print(f"Error: {e}")
