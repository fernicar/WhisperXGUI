# WhisperX GUI Transcription Tool

<!-- ZS:PLATFORM:DESKTOP -->
<!-- ZS:LANGUAGE:PYTHON -->
<!-- ZS:UI:TKINTER -->
<!-- ZS:COMPLEXITY:MEDIUM -->
<!-- ZS:PRIORITY:HIGH -->

## Description

A desktop graphical user interface application designed to facilitate the transcription of audio and video files using the powerful WhisperX engine. This tool simplifies the process of generating accurate transcripts, including optional word-level timestamps and speaker diarization (via WhisperX's capabilities), through a user-friendly interface. It supports various file formats, model sizes, languages, and compute types, making advanced transcription accessible without needing direct command-line interaction.

## Functionality

### Core Features

*   **File Input:** Allows adding multiple audio/video files for batch transcription.
*   **File Management:** Provides options to remove selected files or clear the entire list.
*   **Configuration:**
    *   Selectable transcription model size (e.g., tiny, base, small, medium, large).
    *   Selectable language for transcription (from a predefined list).
    *   Selectable compute type for optimization (e.g., float32, float16, int8).
    *   Option to enable word-level timestamps in the output.
*   **Transcription Process:** Initiates the transcription of all added files sequentially.
*   **Output:** Displays progress and status messages in a dedicated log area.
*   **File Saving:** Automatically saves generated transcripts in both SubRip (.srt) and plain text (.txt) formats.
*   **Output Organization:** Creates timestamped output directories for each input file to keep results organized.
*   **Folder Access:** Automatically opens the output directory upon completion of each file's transcription.

### User Interface

The application presents a single main window.

*   **Layout:** Organized vertically with distinct sections for file input, transcription settings, output log, and action button.
*   **File Input Area:**
    *   Label: "Input Files:"
    *   Listbox: Displays the list of selected files by their base names.
    *   Buttons: "➕ Add Files" to browse and add files, "➖ Remove Selected" to remove the highlighted file, "🆑 Clear All" to empty the list.
*   **Settings Area:**
    *   Labels and Comboboxes for "Model:", "Language:", and "Compute Type:".
    *   Checkbox: "Enable word-level timestamps".
*   **Output Log:**
    *   Scrolled Text Area: Displays messages about loading models, transcription progress, output paths, and errors. Content should automatically scroll to the bottom.
*   **Action Button:**
    *   Large Button: "✨ Transcribe All" to start the transcription process. This button should be disabled while transcription is in progress.
*   **Splash Screen:** A simple, undecorated window is shown upon application startup, displaying a title, a loading message (e.g., "Loading dependencies..."), an indeterminate progress bar, and a status label indicating which component is currently loading. This screen should close automatically once the main window is ready.

### Behavior Specifications

*   Adding files appends their paths to an internal list and updates the listbox display with just the filenames.
*   Removing a file removes it from both the listbox and the internal list.
*   Clearing removes all files.
*   Clicking "Transcribe All" validates that files are selected. If not, an error message is shown.
*   The transcription process runs in a background thread to keep the GUI responsive.
*   Output messages from the background process are safely relayed to the GUI's scrolled text area.
*   For each input file:
    *   An output directory named `transcripts/InputFileName_YYYY-MM-DD_HH-MM` is created.
    *   The `.srt` file format should use `HH:MM:SS,ms` timestamp format.
    *   If word-level timestamps are enabled, the `.srt` output *should not* include special formatting (like HTML font tags for color) around individual words, although the underlying WhisperX engine *will* provide word-level timing data which *can* be included if necessary for advanced processing, but the standard `.srt` format generated *should just be the plain text segment* with start/end timestamps. The example code shows highlighting but the standard `.srt` format doesn't support rich text; therefore, generate standard SRT.
*   Error handling should catch exceptions during the transcription process and report them in the output log and/or a message box.
*   The application should prompt the user for confirmation before closing.

### Language Mapping

The application uses a specific mapping between human-readable language names shown in the dropdown and the language codes required by the transcription engine:

*   English: `en`
*   French: `fr`
*   German: `de`
*   Spanish: `es`
*   Italian: `it`
*   Japanese: `ja`
*   Chinese: `zh`
*   Dutch: `nl`
*   Ukrainian: `uk`
*   Portuguese: `pt`

The GUI should display the human-readable names, but the underlying transcription logic must use the corresponding codes.

## Technical Implementation

### Architecture

*   Desktop application using the Tkinter library for the GUI.
*   Uses threading to perform the computationally intensive transcription task asynchronously, preventing the GUI from freezing.
*   Utilizes a thread-safe queue to pass output messages from the background transcription thread back to the main GUI thread for display.
*   Relies heavily on external libraries for the core transcription engine, model loading, and audio processing.

### Data Structures

*   A Python list (`self.file_list`) holds the absolute paths of the input files.
*   A Python dictionary (`self.language_mapping`) stores the mapping between language names and codes.
*   Task data (segments, words, timestamps) is processed using data structures provided by the transcription library.

### Algorithms

*   File path management (adding, removing, clearing).
*   Queue-based inter-thread communication for GUI updates.
*   Timestamp formatting into `HH:MM:SS,ms` string format.
*   Core transcription and alignment algorithms are handled by the external `whisperx` library.
*   OS-specific commands for opening file explorer windows.

### External Libraries Required

The implementation requires the following Python libraries and their dependencies to be installed in the environment:

*   `torch`: For GPU acceleration and tensor operations (specify version compatible with `whisperx` and CUDA if used, e.g., `torch==2.6.0.dev...` with `cu121` index).
*   `torchaudio`: Companion library for audio processing.
*   `ctranslate2`: Required by `faster-whisper` which WhisperX uses.
*   `faster-whisper`: A reimplementation of Whisper for speed.
*   `nltk`: For text processing, potentially required by alignment models.
*   `pandas`: Data manipulation library, potentially used by dependencies.
*   `pyannote.audio`: For speaker diarization (even if not explicitly exposed in this minimal UI, it's a WhisperX dependency).
*   `setuptools`: Build utility.
*   `transformers`: Hugging Face library, used by WhisperX for models.
*   `whisperx`: The core library for transcription and alignment (specify version, e.g., `whisperx==3.3.2`, noting potential `--no-deps` during its installation as its dependencies are listed separately).

### Implementation Notes

*   Ensure the environment has the necessary deep learning libraries (`torch`, `whisperx`, etc.) installed correctly, ideally with GPU support configured if available.
*   The application requires an **external command-line audio processing tool** to be installed and accessible in the system's PATH for the underlying transcription library (`whisperx`) to load audio files. If this external tool is not found, the application may fail during the "Load audio" step with a non-descriptive error message (e.g., `RuntimeError`) that does not explicitly mention the missing dependency. Users should ensure this fundamental audio utility is installed on their operating system.
*   Handle potential `ImportError` exceptions gracefully during startup if required Python libraries are missing, ideally informing the user which dependency is needed. The splash screen includes basic status updates during imports.
*   Clean up model resources (unload models, clear CUDA cache) after each file and after processing all files to free up memory.

## Getting Started (for the user using the LLM tool)

1.  Ensure you have Python installed (version 3.8 or higher recommended).
2.  Ensure the necessary **external command-line audio processing tool** is installed on your operating system and available in your system's PATH. (This is the dependency mentioned in Implementation Notes that, if missing, causes cryptic errors).
3.  Prepare your environment by installing the required Python libraries. You may need to use a virtual environment. The libraries are listed in the "External Libraries Required" section. Specific installation commands or a `requirements.txt` file derived from the list may be needed depending on the LLM tool's capabilities. Pay attention to specific version or index-url requirements for `torch`.
4.  Use your Zero Source LLM tool to generate the application code based on this README.
5.  Run the generated Python script (`main.py`).

## Testing Scenarios

1.  Run the application and verify the splash screen appears correctly, then closes to show the main window.
2.  Add several different audio/video files. Verify they appear in the listbox.
3.  Remove one file. Verify it is removed from the list.
4.  Click "Clear All". Verify the list is empty.
5.  Add one audio file. Select a model (e.g., 'small'), a language (e.g., 'English'), compute type ('float16'), and enable word timestamps. Click "Transcribe All".
    *   Verify the button becomes disabled.
    *   Verify output messages appear in the log area indicating progress.
    *   Verify that upon completion, a new directory is created in a `transcripts` folder with a timestamped name matching the input file.
    *   Verify `.srt` and `.txt` files are created in that directory.
    *   Open the `.srt` file and verify the content includes timestamps and text segments.
    *   Open the `.txt` file and verify it contains the plain text transcription.
    *   Verify the output directory is automatically opened by the system file explorer.
    *   Verify the "Transcribe All" button becomes enabled again.
6.  Repeat step 5 with a different language and without word timestamps.
7.  Attempt to transcribe with no files added. Verify an error message is shown.
8.  Test closing the application and verify the confirmation prompt appears.

## Security Considerations

*   The application processes local files only.
*   It loads models and potentially other resources over the network using the underlying libraries. Standard network security practices apply to the environment where the application is run.
*   No user data is stored or transmitted externally by this application itself. Data storage is local to the user's machine.

## Compatibility

*   Designed for desktop operating systems (Windows, macOS, Linux) where Tkinter and the required external libraries (including the command-line audio tool) can be installed and run.
*   The core transcription functionality relies on the compatibility of the `whisperx` library and its dependencies with the user's hardware and operating system, particularly concerning CUDA support for GPU acceleration.

## Conclusion

This README provides a comprehensive description of the WhisperX GUI Transcription Tool. By following these specifications, an LLM can generate the necessary Python code to create a functional application that wraps the powerful WhisperX library, offering an accessible way for users to transcribe audio and video files. The emphasis on clear functionality, technical structure, and necessary external dependencies (including the note about the crucial, unnamed audio processing tool) guides the generation process while adhering to the Zero Source paradigm.