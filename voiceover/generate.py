import argparse
import datetime
import os
import pkgutil
import numpy as np
import soundfile as sf
import mlx.core as mx
from f5_tts_mlx.cfm import F5TTS
from f5_tts_mlx.utils import convert_char_to_pinyin
from voiceover.transcript import generate_chunked_transcript
import strip_markdown
from voiceover.sample import sample_guide_prompt

# Constants
SAMPLE_RATE = 24_000
HOP_LENGTH = 256
FRAMES_PER_SEC = SAMPLE_RATE / HOP_LENGTH
TARGET_RMS = 0.1


def read_and_generate_chunked_transcript(file_path, **kwargs):
    """Reads and splits the input text file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = strip_markdown.strip_markdown(file.read())
    transcript_chunks = generate_chunked_transcript(content=file_content, **kwargs)
    return transcript_chunks


def load_pretrained_model(model_name):
    """Loads the pre-trained model and applies quantization."""
    f5tts = F5TTS.from_pretrained(model_name)
    return f5tts


def handle_reference_audio(ref_audio_path=None, ref_text=None):
    """Handles reference audio loading."""
    if ref_audio_path is None:
        data = pkgutil.get_data("f5_tts_mlx", "tests/test_en_1_ref_short.wav")
        
        tmp_ref_audio_file = "/tmp/ref.wav"
        with open(tmp_ref_audio_file, "wb") as f:
            f.write(data)
        
        audio, sr = sf.read(tmp_ref_audio_file)
        if ref_text is None:
            raise ValueError("Reference text must be provided when using default reference audio.")
    else:
        audio, sr = sf.read(ref_audio_path)
        if sr != SAMPLE_RATE:
            raise ValueError("Reference audio must have a sample rate of 24kHz")

    audio = mx.array(audio)
    ref_audio_duration = audio.shape[0] / SAMPLE_RATE
    print(f"Got reference audio with duration: {ref_audio_duration:.2f} seconds")

    # Normalize RMS if necessary
    rms = mx.sqrt(mx.mean(mx.square(audio)))
    if rms < TARGET_RMS:
        audio = audio * TARGET_RMS / rms

    return audio, ref_text


def read_transcript_list(transcripts, output_dir, f5tts, audio, ref_audio_text, steps, method, speed, cfg_strength, sway_sampling_coef):
    """
    Reads transcripts, generates audio for each transcript,
    and returns the concatenated audio.
    """
    os.makedirs(output_dir, exist_ok=True)
    all_waves = []

    for i, transcript in enumerate(transcripts):
        full_text = ref_audio_text + " " + transcript
        pinyin_text = convert_char_to_pinyin([full_text])

        start_date = datetime.datetime.now()
        
        wave, _ = f5tts.sample(
            mx.expand_dims(audio, axis=0),
            text=pinyin_text,
            duration=None,
            steps=steps,
            method=method,
            speed=speed,
            cfg_strength=cfg_strength,
            sway_sampling_coef=sway_sampling_coef,
            seed=None,
        )
        # Trim the reference audio
        wave = wave[audio.shape[0]:]
        generated_duration = wave.shape[0] / SAMPLE_RATE
        elapsed_time = datetime.datetime.now() - start_date
        print(f"Generated {generated_duration:.2f} seconds of audio for transcript {i+1} in {elapsed_time}")

        all_waves.append(wave)

    return np.concatenate(all_waves)


def save_audio(final_wave, output_path):
    """Saves the final waveform to an audio file."""
    sf.write(output_path, np.array(final_wave), SAMPLE_RATE)
    print(f"Audio saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate audio from a transcript file.")
    
    # Required arguments
    parser.add_argument('--input-file', '-i', type=str, required=True,
                        help='Path to the input text file containing the transcript.')
    parser.add_argument('--ref-audio', '-ra', type=str, default=None, 
                        help='Optional path to the reference audio file. If not provided, uses a default test audio.')
    parser.add_argument('--ref-text', '-rt', type=str, default="Some call me nature, others call me mother nature.",
                        help='Reference text corresponding to the reference audio.')
    parser.add_argument('--output-dir', '-o', type=str, default='./',
                        help='Directory where the output audio will be saved.')

    # Additional parameters for audio generation
    parser.add_argument('--steps', type=int, default=32,
                        help='Number of sampling steps.')
    parser.add_argument('--method', type=str, choices=['euler', 'midpoint'], default='euler',
                        help='Sampling method.')
    parser.add_argument('--speed', type=float, default=0.8,
                        help='Speed factor for audio generation.')
    parser.add_argument('--cfg-strength', type=float, default=2.0,
                        help='Strength of configuration guidance.')
    parser.add_argument('--sway-sampling-coef', type=float, default=-1.0,
                        help='Coefficient for sway sampling.')

    # Additional parameters for generating transcripts
    parser.add_argument('--repo', type=str, default="mlx-community/Qwen2.5-Coder-7B-Instruct-4bit",
                        help='Model repository name.')
    parser.add_argument('--guide-prompt', type=str, default=sample_guide_prompt,
                        help='Guide prompt for model generation.')
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='Enable verbose mode.')
    parser.add_argument('--max-tokens', type=int, default=10000,
                        help='Maximum number of tokens.')
    parser.add_argument('--top-p', type=float, default=0.8,
                        help='Top p value for token selection.')
    parser.add_argument('--temp', type=float, default=0.,
                        help='Temperature value for randomness.')

    # Additional parameter for pretrained model
    parser.add_argument('--pretrained-model', type=str, default="alandao/f5-tts-mlx-4bit",
                        help='Pre-trained model name.')

    parser.add_argument('--raw-mode', action="store_true", default=False,
                        help='Pre-trained model name.')
    args = parser.parse_args()
    
    # Pass additional arguments related to transcript generation
    kwargs = {
        'repo': args.repo,
        'guide_prompt': args.guide_prompt,
        'verbose': args.verbose,
        'max_tokens': args.max_tokens,
        'top_p': args.top_p,
        'temp': args.temp,
    }
    
    if args.raw_mode is False:
        transcripts = read_and_generate_chunked_transcript(args.input_file, **kwargs)
    else:
        with open(args.input_file) as file:
            transcripts = file.read().split("\n\n")
        print("Directly read file and will generate",transcripts)
    f5tts = load_pretrained_model(model_name=args.pretrained_model)
    audio, ref_audio_text = handle_reference_audio(ref_audio_path=args.ref_audio, ref_text=args.ref_text)
    final_wave = read_transcript_list(
        transcripts, args.output_dir, f5tts, audio, ref_audio_text,
        args.steps, args.method, args.speed, args.cfg_strength, args.sway_sampling_coef
    )
    final_output_path = os.path.join(args.output_dir, "output.wav")
    save_audio(final_wave, final_output_path)
    
    
if __name__ == "__main__":
    main()
