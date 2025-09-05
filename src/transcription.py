import time

from faster_whisper import WhisperModel


def setup_model():
    # <<< Choose the Whisper model size >>>
    # Options: "tiny", "base", "small", "medium", "large"
    # Smaller models are faster and use less memory/VRAM, but are less accurate.
    # Larger models are more accurate but slower and require more resources.
    # Start with "base" or "small" and see how it performs on your machine.
    # Add ".en" for English-only models (e.g., "base.en"), which might be faster/better if you only need English.
    MODEL_SIZE = "small"

    # --- Load the Whisper model ---
    # This will download the model weights the first time you use a specific size.
    # Whisper automatically detects if a compatible GPU (CUDA) is available and uses it.
    # You can force CPU with device="cpu" argument if needed.
    print(f"Loading Whisper model '{MODEL_SIZE}'...")
    try:
        model = WhisperModel(MODEL_SIZE, device="cuda", compute_type="float16")
        print(f"Model '{MODEL_SIZE}' loaded successfully.")
        if model.device == "cuda":
            print("Whisper is using GPU (CUDA).")
        else:
            print(f"Whisper is using {model.device}.")

        return model

    except Exception as e:
        msg = f"Error loading Whisper model: {e}. Ensure faster-whisper and a CUDA-compatible torch are installed."
        print(msg)
        raise Exception(msg)


def transcribe(audio_file_path: str, language_code: str, verbose=False):
    model = setup_model()

    # --- Transcribe the audio ---
    print(f"Starting transcription for '{audio_file_path}'...")
    start_time = time.time()

    model_task = "transcribe" if language_code == "en" else "translate"

    segments, info = model.transcribe(
        audio_file_path, language=language_code, task=model_task, beam_size=5
    )

    segment_list = []
    for segment in segments:
        segment_list.append(
            {"start": segment.start, "end": segment.end, "text": segment.text}
        )
        if verbose:
            print(
                f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text.strip()}"
            )

    result = {
        "text": " ".join([s["text"].strip() for s in segment_list]),
        "segments": segment_list,
        "language": info.language,
    }

    end_time = time.time()
    duration = end_time - start_time
    print(f"\nTranscription finished in {duration:.2f} seconds.")

    return result


if __name__ == "__main__":
    path = "/test_files/agrinews_July_30th_2025.mp3"
    transcribe(path, "pt")
