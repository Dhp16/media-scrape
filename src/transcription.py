import whisper
import time  # To measure transcription time


def setup_model():
    # <<< Choose the Whisper model size >>>
    # Options: "tiny", "base", "small", "medium", "large"
    # Smaller models are faster and use less memory/VRAM, but are less accurate.
    # Larger models are more accurate but slower and require more resources.
    # Start with "base" or "small" and see how it performs on your machine.
    # Add ".en" for English-only models (e.g., "base.en"), which might be faster/better if you only need English.
    MODEL_SIZE = "base"

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


def transcribe(audio_file_path: str, language_code: str, verbose=False):
    model = setup_model()

    # --- Transcribe the audio ---
    print(f"Starting transcription for '{audio_file_path}'...")
    start_time = time.time()

    model_task = "transcribe" if language_code == "en" else "translate"

    result = model.transcribe(
        audio_file_path, language=language_code, task=model_task, verbose=verbose
    )

    end_time = time.time()
    duration = end_time - start_time
    print(f"\nTranscription finished in {duration:.2f} seconds.")

    return result


if __name__ == "__main__":
    path = "/test_files/agrinews_July_30th_2025.mp3"
    transcribe(path, "pt")
