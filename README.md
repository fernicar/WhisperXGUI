![preview1](https://github.com/fernicar/WhisperXGUI/blob/main/images/app_capture0.png)
![preview2](https://github.com/fernicar/WhisperXGUI/blob/main/images/app_capture1.png)

# WhisperX GUI

A graphical user interface for WhisperX that provides easy-to-use audio and video transcription capabilities.

## Features

- Support for multiple audio and video formats (mp4, mkv, mov, wmv, avi, flv, mp3, wav, aac, flac, ogg)
- Multiple language support including English, French, German, Spanish, Italian, Japanese, Chinese, Dutch, Ukrainian, and Portuguese
- Various WhisperX model options (tiny, base, small, medium, large-v2)
- Different compute types (float32, float16, int8)
- Word-level timestamps for precise word highlighting in SRT files (using WhisperX's phoneme-based alignment)
- Batch processing of multiple files
- Automatic output directory creation with timestamps
- Generates both SRT and TXT output formats
- CUDA support for GPU acceleration
- Progress tracking and status updates
- Automatic output folder opening after completion

## Requirements

- Python 3.x
- CUDA-capable GPU (optional, for faster processing)
- Required Python packages (key dependencies):
  - tkinter (included with Python)
  - whisperx==3.3.2
  - torch==2.6.0+cu121
  - torchaudio

## Installation

1. Clone this repository
2. Create a virtual environment (recommended)
3. Install the required dependencies:
```bash
pip install -r requirements.txt
pip install -U whisperx==3.3.2 --no-deps
```

### Note on Dependencies

The installation process is somewhat complex due to dependency conflicts. WhisperX officially requires:

```
ctranslate2
faster-whisper
nltk
pandas
pyannote.audio
setuptools
torch
torchaudio
transformers
```

However, there are several compatibility issues:

- WhisperX requires `torchaudio>=2` but may not recognize development versions like `2.5.0.dev20241112+cu121`
- Using `--no-deps` with WhisperX installation is necessary to prevent it from downgrading or conflicting with other packages
- The PyTorch nightly build with CUDA 12.1 (cu121) is specified in requirements.txt
- If you need to use a different CUDA version, you'll need to modify the requirements.txt file and ensure compatibility with all dependencies
- The specific PyTorch index URL in requirements.txt (`https://download.pytorch.org/whl/nightly/cu121`) is crucial for getting the correct CUDA-enabled versions

The current setup represents a working configuration but may need adjustments based on your specific environment.

### Custom Installation

If you need to use different versions (e.g., a different CUDA version or stable PyTorch instead of nightly), you can create your own custom requirements file:

1. Create a file named `custom_requirements.txt` with your desired dependencies
2. Install using your custom file instead of the provided one

```bash
pip install -r custom_requirements.txt
pip install -U whisperx==3.3.2 --no-deps
```

Example `custom_requirements.txt` for stable PyTorch with CUDA 11.8:

```
--index-url https://download.pytorch.org/whl/cu118
torch==2.1.2
torchaudio==2.1.2
ctranslate2>=4.5.0
faster-whisper==1.1.0
nltk
pandas
pyannote.audio==3.3.2
setuptools>=65
transformers
```

Example for CPU-only installation:

```
torch==2.1.2
torchaudio==2.1.2
ctranslate2>=4.5.0
faster-whisper==1.1.0
nltk
pandas
pyannote.audio==3.3.2
setuptools>=65
transformers
```

Note that performance and compatibility may vary with different configurations.

### Testing CUDA Availability

To verify that CUDA is properly installed and available to PyTorch, you can run the included test script:

```bash
python tools/testCuda.py
```

This will display information about your CUDA installation and available GPUs. If CUDA is properly configured, you should see output similar to:

```
CUDA is available. You can use GPU for acceleration.
Number of GPUs available: 1
GPU name: NVIDIA GeForce RTX 3080
```

If CUDA is not available, the script will indicate that you need to check your GPU drivers and CUDA installation.

## Usage

1. Run the application:
```bash
python main.py
```

2. Use the interface to:
   - Add files using the "Add Files" button
   - Select your desired model size
   - Choose the target language
   - Select compute type
   - Click "Transcribe All" to begin processing

3. Output files will be automatically saved in a `transcripts` directory with the following naming format:
   - `{original_filename}_{timestamp}/{original_filename}.srt`
   - `{original_filename}_{timestamp}/{original_filename}.txt`

## Notes

- This application is currently a proof of concept and is under active development
- For optimal performance, using a CUDA-capable GPU is recommended
- The medium model is set as default for a balance of speed and accuracy
- Word-level timestamps are generated using WhisperX's two-step process:
  1. First, audio is transcribed using Whisper
  2. Then, the transcription is aligned with the audio using a phoneme-based ASR model (like wav2vec2) to get accurate word-level timestamps
- The application has numerous dependencies that are automatically installed through the requirements.txt file
- The dependency configuration may need adjustments for different environments

### Current Environment

This application has been successfully tested with the following environment. This is not a definitive list of requirements but rather a snapshot of a working configuration:

<details>
<summary>Click to expand full dependency list working for me</summary>

```
aiohappyeyeballs        2.6.1
aiohttp                 3.11.18
aiosignal               1.3.2
alembic                 1.15.2
antlr4-python3-runtime  4.9.3
asteroid-filterbanks    0.4.0
attrs                   25.3.0
av                      14.3.0
certifi                 2025.1.31
cffi                    1.17.1
charset-normalizer      3.4.1
click                   8.1.8
colorama                0.4.6
coloredlogs             15.0.1
colorlog                6.9.0
contourpy               1.3.2
ctranslate2             4.6.0
cycler                  0.12.1
docopt                  0.6.2
einops                  0.8.1
faster-whisper          1.1.0
filelock                3.18.0
flatbuffers             25.2.10
fonttools               4.57.0
frozenlist              1.6.0
fsspec                  2025.3.2
greenlet                3.2.1
huggingface-hub         0.30.2
humanfriendly           10.0
HyperPyYAML             1.2.2
idna                    3.10
Jinja2                  3.1.6
joblib                  1.4.2
julius                  0.2.7
kiwisolver              1.4.8
lightning               2.5.1
lightning-utilities     0.14.3
Mako                    1.3.10
markdown-it-py          3.0.0
MarkupSafe              3.0.2
matplotlib              3.10.1
mdurl                   0.1.2
mpmath                  1.3.0
multidict               6.4.3
networkx                3.4.2
nltk                    3.9.1
numpy                   2.2.5
omegaconf               2.3.0
onnxruntime             1.21.1
optuna                  4.3.0
packaging               24.2
pandas                  2.2.3
pillow                  11.2.1
pip                     25.0.1
primePy                 1.3
propcache               0.3.1
protobuf                6.30.2
pyannote.audio          3.3.2
pyannote.core           5.0.0
pyannote.database       5.1.3
pyannote.metrics        3.2.1
pyannote.pipeline       3.0.1
pycparser               2.22
Pygments                2.19.1
pyparsing               3.2.3
pyreadline3             3.5.4
python-dateutil         2.9.0.post0
pytorch-lightning       2.5.1
pytorch-metric-learning 2.8.1
pytz                    2025.2
PyYAML                  6.0.2
regex                   2024.11.6
requests                2.32.3
rich                    14.0.0
ruamel.yaml             0.18.10
ruamel.yaml.clib        0.2.12
safetensors             0.5.3
scikit-learn            1.6.1
scipy                   1.15.2
semver                  3.0.4
sentencepiece           0.2.0
setuptools              79.0.0
shellingham             1.5.4
six                     1.17.0
sortedcontainers        2.4.0
soundfile               0.13.1
speechbrain             1.0.3
SQLAlchemy              2.0.40
sympy                   1.13.1
tabulate                0.9.0
tensorboardX            2.6.2.2
threadpoolctl           3.6.0
tokenizers              0.21.1
torch                   2.6.0.dev20241112+cu121
torch-audiomentations   0.12.0
torch_pitch_shift       1.2.5
torchaudio              2.5.0.dev20241112+cu121
torchmetrics            1.7.1
tqdm                    4.67.1
transformers            4.51.3
typer                   0.15.2
typing_extensions       4.13.2
tzdata                  2025.2
urllib3                 2.4.0
whisperx                3.3.2
yarl                    1.20.0
```
</details>

## Acknowledgments

This project would not be possible without the following open-source projects:

- [WhisperX](https://github.com/m-bain/whisperX) - Time-accurate automatic speech recognition using Whisper with word-level timestamps and speaker diarization
- [OpenAI Whisper](https://github.com/openai/whisper) - The base speech recognition model
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - A faster implementation of Whisper using CTranslate2
- [PyTorch](https://pytorch.org/) - The deep learning framework used
- [pyannote-audio](https://github.com/pyannote/pyannote-audio) - Speaker diarization toolkit
- [CTranslate2](https://github.com/OpenNMT/CTranslate2) - A fast inference engine for Transformer models
- [Hugging Face Transformers](https://github.com/huggingface/transformers) - State-of-the-art Natural Language Processing
- [NLTK](https://www.nltk.org/) - Natural Language Toolkit for text processing
- [SpeechBrain](https://speechbrain.github.io/) - A PyTorch-based speech toolkit

Special thanks to:
- Max Bain and the WhisperX team for developing the core transcription technology
- Guillaume Klein for the faster-whisper implementation
- Hervé Bredin and the pyannote team for their speaker diarization tools
- The PyTorch team for their excellent deep learning framework
- All contributors to the open-source libraries used in this project

## License

[MIT License](LICENSE)