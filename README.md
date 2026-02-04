# XTracer Quick Start (Android Dynamic Analysis)

This repo automates dynamic analysis of Android APKs using Frida on an emulator. It installs an APK, injects Frida hooks, (optionally) drives UI events, and exports per-thread JSON traces.

## Prerequisites
- Android SDK (adb, build-tools `aapt` available on PATH)
- Python 3.8+
- `pip install frida-tools` (provides `frida-ps`)
- Frida server for your emulator architecture (e.g., `android-x86_64`), placed on your PC

## Configure
Edit `config/config.yml`:
- `device_serial`: your AVD device, e.g., `emulator-5554`
- `apk_dir`: folder containing APKs to analyze (create `apks/` and drop files in)
- `hook_mode`: `single` or `mult`
- `use_monkey`: `false` by default (requires jars on device)
- `frida_server_host_path`: absolute path to frida-server on your PC

## Run
1. Start your AVD (Android Studio → Device Manager or `emulator -avd <name>`)
2. Start checker: `python XT_checker.py` (sets port forwards and starts frida-server)
3. Place APKs in `apks/` (e.g., `apks/com.citiesquiz.nearme.gamecenter.apk`)
4. Run tracing: `python XTracer.py`
5. Logs: `<apk_dir>/feature/<apk>.txt` (JSON map `tid` → `[class, methodSignature, args[]]`)

## Notes
- Hook list: `source/hook_list_479.csv` (first column; header dropped)
- Frida script: `XTracer.js` sends `XTracer:::{cmd:'log'|'enter'}` and "Hook Complete" once ready
- Dataset utilities: `XT_read_log.py` converts logs to frequency/sequence CSVs
