# AI Agent Instructions for XTracer

These instructions orient AI coding agents to be productive in this codebase. Focus on the current, observable patterns and workflows.

## Big Picture
- Purpose: Automate dynamic analysis of Android APKs via Frida on an emulator (BlueStacks) to capture API-call traces and derive features/datasets.
- Flow: Python orchestrates install → launch → Frida hook → Monkey-driven interaction → log export → uninstall. Frida JS defines hooks; data is written as JSON per app.

## Key Components
- Orchestrator: XTracer.py — manages APK metadata (via `aapt`), install/run (via `adb`), Frida injection of XTracer.js, message handling, and JSON export.
- Frida Script: XTracer.js — hooks methods from `source/hook_list_479.csv` (+ `extend_list`), sends messages like `XTracer:::{ cmd: 'enter' | 'log' }` and signals `Hook Complete`.
- Device/Frida Setup: XT_checker.py — starts emulator (from `config/config.yml`), maintains `adb` connection/port-forward, and starts `frida-server` via `source/frida-server_start.bat`.
- Config IO: XT_config.py — YAML wrapper used for simple persistence (both `config/config.yml` and run storage YAML in XTracer.py).
- Dataset Tools: XT_read_log.py — converts per-thread JSON traces into frequency/sequence CSV datasets using `source/hook_list_479.csv` and optional `tmp/permission_intent_header.csv`.
- Data & Scripts: `config/` (emulator settings), `source/hook_list_479.csv` (API list), `source/frida-server_start.bat` (on-device frida start), `tmp/permission_intent_header.csv` (intent/permission headers).

## Workflow
1. Configure emulator path/IP in `config/config.yml` (BlueStacks by default).
2. Ensure `adb`, `aapt`, and `frida` CLI are on PATH; device has `monkey.jar` and `framework.jar` under `/sdcard/`.
3. Start emulator and frida server: run `python XT_checker.py` to connect, forward ports, and launch frida-server.
4. Set `chooseApkPath` (and `hook_mode`) in `XTracer.py` to the folder of APKs to process.
5. Run `python XTracer.py` to iterate apps: install, start, attach Frida, run Monkey for ~2 minutes, export JSON, uninstall.
6. Find per-app JSON traces under `<chooseApkPath>/feature/<apk>.txt` (maps `tid` → `[class, methodSignature, args[]]`).
7. Optionally generate datasets with `XT_read_log.py` (update its hard-coded paths `target_path`/outputs before use).

## Conventions & Patterns
- Paths: Windows-style and often absolute; update `chooseApkPath` and dataset/config paths before executing.
- Hook list: `source/hook_list_479.csv` first row is header; code drops it and uses the first column.
- Frida messaging: JSON payload prefixed by `XTracer:::` with `cmd` = `log` or `enter`. `Hook Complete` marks hook readiness.
- Child processes: Frida enables `session.enable_child_gating()` and `device.on('child-added', ...)` to hook spawned processes.
- Storage YAML: XTracer.py writes detection status counts and per-app success/fail to a YAML at `<chooseApkPath>/0000_storage.yml` via `XT_config.config`.

## Commands (observed)
- Emulator/frida setup: `python XT_checker.py` (handles `adb connect`, port forwarding, frida start).
- Tracing loop: `python XTracer.py` (requires `frida-ps -U` connected and `aapt` available).
- On-device frida server script: executed by checker via `adb shell < source/frida-server_start.bat` (depends on device shell behavior).

## Integration Notes
- APK metadata: `aapt dump badging` is parsed to get label, package, and main activity.
- Frida attach: `frida.get_usb_device().enumerate_processes()` filters by `packageName`/label before `session.create_script` of `XTracer.js`.
- Monkey: runs `tv.panda.test.monkey.Monkey` via `app_process` for UI events; expects jars under `/sdcard/`.

## Gotchas
- XT_read_log.py uses `E:\...` paths; update to workspace-relative or config-driven before using.
- Frida server launch via batch redirection may vary by device; current implementation assumes `su` available.
- PyQt5 `QApplication` is initialized in XTracer.py without GUI usage; keep it unless refactoring threading.
- Ensure `aapt` exists; otherwise package/activity parsing will fail and app is skipped.

## Examples
- Add a hook: update `extend_list` in XTracer.py or add a row to `source/hook_list_479.csv` (format `class/method`).
- Consume logs: `XT_read_log.readJson_frequency(path)` expects `class/method` names derived from `methodSignature.split('(')[0]`.

If anything above is unclear or missing (e.g., your emulator/frida setup differs), tell me what to adjust and I’ll refine this doc.