import whisper
import os
import time  # To measure transcription time


def setup_model():
    # <<< Choose the Whisper model size >>>
    # Options: "tiny", "base", "small", "medium", "large"
    # Smaller models are faster and use less memory/VRAM, but are less accurate.
    # Larger models are more accurate but slower and require more resources.
    # Start with "base" or "small" and see how it performs on your machine.
    # Add ".en" for English-only models (e.g., "base.en"), which might be faster/better if you only need English.
    MODEL_SIZE = "base.en"

    # --- Load the Whisper model ---
    # This will download the model weights the first time you use a specific size.
    # Whisper automatically detects if a compatible GPU (CUDA) is available and uses it.
    # You can force CPU with device="cpu" argument if needed.
    print(f"Loading Whisper model '{MODEL_SIZE}'...")
    try:
        model = whisper.load_model(MODEL_SIZE)
        print(f"Model '{MODEL_SIZE}' loaded successfully.")
        if model.device.type == "cuda":
            print("Whisper is using GPU (CUDA).")
        else:
            print("Whisper is using CPU.")

        return model

    except Exception as e:
        msg = f"Error loading Whisper model: {e}. Ensure PyTorch is installed correctly (with CUDA support if applicable)."
        print(msg)
        raise Exception(msg)


def transcribe(audio_file_path: str):
    model = setup_model()

    # --- Transcribe the audio ---
    print(f"Starting transcription for '{audio_file_path}'...")
    start_time = time.time()

    # Perform the transcription
    # For long audio, this might take a significant amount of time!
    result = model.transcribe(
        audio_file_path, verbose=True
    )  # verbose=True shows progress
    # result = model.transcribe(filepath, language="pt", fp16=False, verbose=True)

    end_time = time.time()
    duration = end_time - start_time
    print(f"\nTranscription finished in {duration:.2f} seconds.")

    # --- Process and Display the Result ---
    print("\n--- Full Transcript ---")
    print(result["text"])

    return result
