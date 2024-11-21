# VoiceOver CLI Tool

The VoiceOver CLI tool converts blog posts written in Markdown into a verbally readable and audible format, making them ideal for creating podcast-like content. You can easily generate high-quality speech audio from your Substack blog posts.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Switching Between Models](#switching-between-models)
  - [Advanced Options](#advanced-options)
- [Arguments](#arguments)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Installation

You can install the VoiceOver CLI tool directly via pip by cloning the repository from GitHub:

```bash
pip install git+https://github.com/tikikun/voiceover.git
```

This command installs all necessary dependencies automatically.

## Usage

The VoiceOver CLI reads a Markdown file containing your blog post, rewrites it into a verbally readable format, and generates speech audio using a pre-trained Text-to-Speech (TTS) model.

### Basic Usage

To generate audio from a Markdown file:

```bash
voiceover --input-file path/to/blog_post.md --output-dir ./outputs/
```

This command reads the content of `blog_post.md`, rewrites it for verbal readability, uses a default reference audio, and saves the generated speech audio as `output.wav` in the specified output directory.

### Switching Between Models

You can switch between 4-bit and 8-bit models by specifying the appropriate pretrained model name:

- **4-bit Model**:

  ```bash
  voiceover --input-file path/to/blog_post.md --pretrained-model alandao/f5-tts-mlx-4bit --output-dir ./outputs/
  ```

- **8-bit Model**:

  ```bash
  voiceover --input-file path/to/blog_post.md --pretrained-model alandao/f5-tts-mlx-8bit --output-dir ./outputs/
  ```

### Advanced Options

#### Reference Audio

Provide a custom reference audio file using the `-ra` option:

```bash
voiceover --input-file path/to/blog_post.md -ra path/to/reference_audio.wav --output-dir ./outputs/
```

#### Sampling Parameters

Adjust sampling parameters such as `steps`, `method`, `speed`, `cfg-strength`, and `sway-sampling-coef`:

```bash
voiceover --input-file path/to/blog_post.md --steps 48 --method midpoint --speed 1.2 --cfg-strength 2.5 --sway-sampling-coef -1.5 --output-dir ./outputs/
```

#### Transcript Generation Parameters

Configure additional parameters used during transcript chunking:

```bash
voiceover --input-file path/to/blog_post.md --repo my-custom-repo --guide-prompt "Custom guide prompt." --verbose --max-tokens 15000 --top-p 0.9 --temp 0.5 --output-dir ./outputs/
```

## Arguments

| Argument               | Type     | Description                                                                 |
|------------------------|----------|-----------------------------------------------------------------------------|
| `--input-file`         | string   | Path to the input Markdown file containing the blog post.                   |
| `--ref-audio`          | string   | Optional path to the reference audio file.                                  |
| `--output-dir`         | string   | Directory where the output audio will be saved.                             |
| `--steps`              | int      | Number of sampling steps for generating audio.                              |
| `--method`             | str      | Sampling method (`euler` or `midpoint`).                                    |
| `--speed`              | float    | Speed factor for audio generation.                                          |
| `--cfg-strength`       | float    | Strength of configuration guidance during sampling.                         |
| `--sway-sampling-coef` | float    | Coefficient for sway sampling.                                              |
| `--repo`               | string   | Model repository name used for chunking transcripts.                        |
| `--guide-prompt`       | string   | Guide prompt for model generation.                                        |
| `--verbose`            | boolean  | Enable verbose mode for detailed logging.                                   |
| `--max-tokens`         | int      | Maximum number of tokens for each chunked transcript.                       |
| `--top-p`              | float    | Top p value for token selection during transcript generation.                 |
| `--temp`               | float    | Temperature value controlling randomness during transcript generation.        |
| `--pretrained-model`   | string   | Pre-trained TTS model name to load. Choose between `alandao/f5-tts-mlx-4bit` and `alandao/f5-tts-mlx-8bit`.|

## Examples

- **Basic Example**: Generate audio from a Markdown file without any additional options.

  ```bash
  voiceover --input-file example_blog_post.md --output-dir results/
  ```

- **Using 8-bit Model**: Specify the 8-bit model for higher quality but potentially larger resource consumption.

  ```bash
  voiceover --input-file example_blog_post.md --pretrained-model alandao/f5-tts-mlx-8bit --output-dir results/
  ```

- **Custom Reference Audio**: Use a specific WAV file as the reference audio.

  ```bash
  voiceover --input-file example_blog_post.md --ref-audio my_reference_audio.wav --output-dir results/
  ```

- **Advanced Configuration**: Customize various parameters for better control over the audio generation process.

  ```bash
  voiceover --input-file example_blog_post.md --steps 64 --method midpoint --speed 1.5 --cfg-strength 2.8 --sway-sampling-coef -2.0 --output-dir results/
  ```

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE.md) for more information.
