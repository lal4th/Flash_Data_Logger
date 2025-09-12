## Flash Data Logger — Requirements

### Scope

- **Goal**: PC application to acquire, display, and log data from a PicoScope oscilloscope, with initial focus on the PicoScope 4262 and continuous logging. [[memory:8854466]]
- **Primary features**: Device detection and initialization, live plotting, CSV recording, device-aware controls and validation, robust shutdown.
- **Initial device focus**: PicoScope 4262 via ps4000 API; support for additional PicoScope models later.

### Environment and Setup

- **OS**: Windows 10+ (64-bit).
- **Runtime**: Python 3.x with virtual environment; dependencies installed from `requirements.txt`.
- **GUI**: PyQt6 with pyqtgraph.
- **SDK**: PicoSDK installed locally; device connected via USB; PicoScope desktop application must be closed during app use. [[memory:8854466]]
- **Entry point**: `python -m app.main` (e.g., `.venv\Scripts\python.exe -m app.main`).

### Architecture

- **Acquisition sources**:
  - **Pico ps4000 block-mode source**: reliable baseline connectivity and data reads.
  - **Pico ps4000 streaming source**: preferred for continuous logging (uses `ps4000RunStreaming` + `ps4000GetStreamingLatestValues` with callback and per-channel overview buffers).
  - **Dummy sine source**: development fallback.
- **Core**: `AppController` orchestrates acquisition loop, processing pipeline, and storage.
- **Processing**: lightweight transform pipeline on scalar samples.
- **Storage**: `CsvWriter` appends timestamp,value rows.
- **UI**: Left control panel, right live plot, status line.

### Device Connectivity and Detection

- **Start behavior**:
  - Always attempt to initialize the Pico source on Start.
  - Prefer reliable block-mode initialization first; attempt streaming next; fallback to dummy if both fail.
  - Do not block Start based solely on wrapper detection; attempt direct DLL initialization even if wrappers fail.
- **Detection**:
  - Provide a non-blocking `probe_device()` that calls detection helpers for user feedback without preventing Start.
  - Add DLL search paths for common PicoSDK install locations and scan the Pico install tree for `ps4000.dll`.
  - Preload core DLLs if present to aid loader resolution.
- **Diagnostics**:
  - Surface full exceptions and driver status codes/names in the Status label on failure (e.g., `PICO_NOT_FOUND (3)`, `PICO_INVALID_PARAMETER (13)`).
  - On success, Status should read “Using Pico source (ps4000)” or “Using Pico source (ps4000 streaming)”.

### Acquisition and Data Flow

- **Streaming mode (preferred for logging)**:
  - Use `ps4000RunStreaming(&sampleInterval, timeUnits, …)`; read back actual interval to compute effective sample rate.
  - Use `ps4000SetDataBuffer` for each active channel and `ps4000GetStreamingLatestValues` with a stdcall callback to copy new chunks from the overview buffer.
  - Maintain an internal ring buffer; throttle UI plot updates to ~30 FPS.
  - Default configuration: Channel A, DC coupling, ±5 V range, 16-bit resolution, sample rate configurable. [[memory:8854466]]
- **Block mode (baseline)**:
  - Determine a valid timebase via `ps4000GetTimebase2`/`ps4000GetTimebase`; run block captures and stream into the ring buffer.
- **Sample representation**:
  - Convert ADC counts to volts using selected input range and `max_adc = 32767`.
  - Provide timestamp for each sample using a monotonic clock (`time.perf_counter`).

### UI Requirements

- **Controls panel** must expose, with device-aware validation and clamping:
  - **Channel**: A/B.
  - **Coupling**: AC/DC.
  - **Voltage range**: list of supported ranges for ps4000 (e.g., ±10 mV … ±20 V).
  - **Resolution**: up to 16-bit for 4262.
  - **Sample rate**: editable/choosable with min/max based on device constraints; clamp and report when adjusted.
- **Record to CSV**: toggle; filename picker; when enabled, write timestamp,value rows continuously.
- **Status line**: show detection info on launch and detailed source/diagnostic messages on Start; do not overwrite detailed errors with generic “Running…”.

### Validation and Error Handling

- **Device-aware limits**:
  - Clamp sample rate to safe device ranges; emit concise message when clamped.
  - Disable or reject invalid UI combinations; display succinct validation errors.
- **Robustness**:
  - Handle missing DLLs by adding search paths and reporting the exact paths tried.
  - Surface full exception text for initialization failures and continue with dummy source if needed.

### CSV Recording

- **Format**: CSV with headerless rows `timestamp,value`.
- **Behavior**: When enabled, write each processed sample; ensure file is properly closed on Stop/exit.

### Live Plot

- **Display**: pyqtgraph plot; light grid; single trace.
- **Update rate**: ~30 FPS; keep last ~5 seconds visible by default.

### Shutdown and Lifecycle

- **Clean shutdown**:
  - Ensure acquisition thread(s) stop on Stop and application exit.
  - Close Pico device handles (`Stop`, `CloseUnit`) even on exceptions.
  - Avoid Qt teardown errors (e.g., “wrapped C/C++ object … deleted”) by stopping acquisition on `QApplication.aboutToQuit`.

### Non-functional Requirements

- **Reliability**: Block mode must provide consistent connectivity as a baseline; streaming added without regressing connectivity.
- **Performance**: UI remains responsive at configured rates; minimal CPU overhead via chunked updates and ring buffer.
- **Extensibility**: Acquisition layer structured to add future Pico families (e.g., ps4000a) without UI changes.

### Acceptance Criteria

- On launch, Status shows detection info; Start always attempts Pico init.
- After Start with device connected and PicoScope desktop app closed:
  - Status reads “Using Pico source (ps4000)” or “Using Pico source (ps4000 streaming)”.
  - Live plot shows device data that changes with probe input.
  - Changing sample rate applies and clamps within device limits.
  - CSV records `timestamp,value` from the active Pico source.
  - No crashes on close; acquisition stops cleanly.

### Priorities (feedback-driven)

1) **Connectivity first**: Ensure reliable ps4000 block-mode connection and data acquisition before any further enhancements.
2) **Diagnostics**: Clear status messages with exact errors and driver codes; improved DLL discovery.
3) **Streaming**: Implement correct callback-based streaming for long logging sessions.
4) **Validation/UI polish**: Device-aware limits and concise errors.
5) **Multi-device support**: Abstract acquisition to accommodate additional Pico models/APIs later. [[memory:8854466]]

### Open Items / Future Work

- ps4000 streaming: tune parameters and buffer sizes per device limits; expose effective sample rate in UI.
- ps4000a and other families: conditional loading and capability discovery.
- Unit/integration tests around acquisition lifecycle and CSV output.


