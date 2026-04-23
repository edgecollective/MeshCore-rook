## About MeshCore

MeshCore is a lightweight, portable C++ library that enables multi-hop packet routing for embedded projects using LoRa and other packet radios. It is designed for developers who want to create resilient, decentralized communication networks that work without the internet.

## 🔍 What is MeshCore?

MeshCore now supports a range of LoRa devices, allowing for easy flashing without the need to compile firmware manually. Users can flash a pre-built binary using tools like Adafruit ESPTool and interact with the network through a serial console.
MeshCore provides the ability to create wireless mesh networks, similar to Meshtastic and Reticulum but with a focus on lightweight multi-hop packet routing for embedded projects. Unlike Meshtastic, which is tailored for casual LoRa communication, or Reticulum, which offers advanced networking, MeshCore balances simplicity with scalability, making it ideal for custom embedded solutions., where devices (nodes) can communicate over long distances by relaying messages through intermediate nodes. This is especially useful in off-grid, emergency, or tactical situations where traditional communication infrastructure is unavailable.

## ⚡ Key Features

* Multi-Hop Packet Routing
  * Devices can forward messages across multiple nodes, extending range beyond a single radio's reach.
  * Supports up to a configurable number of hops to balance network efficiency and prevent excessive traffic.
  * Nodes use fixed roles where "Companion" nodes are not repeating messages at all to prevent adverse routing paths from being used.
* Supports LoRa Radios – Works with Heltec, RAK Wireless, and other LoRa-based hardware.
* Decentralized & Resilient – No central server or internet required; the network is self-healing.
* Low Power Consumption – Ideal for battery-powered or solar-powered devices.
* Simple to Deploy – Pre-built example applications make it easy to get started.

## 🎯 What Can You Use MeshCore For?

* Off-Grid Communication: Stay connected even in remote areas.
* Emergency Response & Disaster Recovery: Set up instant networks where infrastructure is down.
* Outdoor Activities: Hiking, camping, and adventure racing communication.
* Tactical & Security Applications: Military, law enforcement, and private security use cases.
* IoT & Sensor Networks: Collect data from remote sensors and relay it back to a central location.

## 🚀 How to Get Started

- Watch the [MeshCore Intro Video](https://www.youtube.com/watch?v=t1qne8uJBAc) by Andy Kirby.
- Watch the [MeshCore Technical Presentation](https://www.youtube.com/watch?v=OwmkVkZQTf4) by Liam Cottle.
- Read through our [Frequently Asked Questions](./docs/faq.md) and [Documentation](https://docs.meshcore.io).
- Flash the MeshCore firmware on a supported device.
- Connect with a supported client.

For developers;

- Install [PlatformIO](https://docs.platformio.org) in [Visual Studio Code](https://code.visualstudio.com).
- Clone and open the MeshCore repository in Visual Studio Code.
- See the example applications you can modify and run:
  - [Companion Radio](./examples/companion_radio) - For use with an external chat app, over BLE, USB or WiFi.
  - [KISS Modem](./examples/kiss_modem) - Serial KISS protocol bridge for host applications. ([protocol docs](./docs/kiss_modem_protocol.md))
  - [Simple Repeater](./examples/simple_repeater) - Extends network coverage by relaying messages.
  - [Simple Room Server](./examples/simple_room_server) - A simple BBS server for shared Posts.
  - [Simple Secure Chat](./examples/simple_secure_chat) - Secure terminal based text communication between devices.
  - [Simple Sensor](./examples/simple_sensor) - Remote sensor node with telemetry and alerting.

The Simple Secure Chat example can be interacted with through the Serial Monitor in Visual Studio Code, or with a Serial USB Terminal on Android.

## 🔨 Building the Rook variant (this fork)

This fork of `meshcore-dev/MeshCore` adds a **`rook`** board variant under `variants/rook/`.

Rook is a Pro Micro nRF52840 board paired with an SX1262 LoRa radio, with GPS plus AHTx0 / BME280 / BMP280 environmental sensors wired on the standard I²C pins. See `variants/rook/platformio.ini` for the full pin map and feature flags.

### Available build environments

The rook variant defines five PlatformIO envs in `variants/rook/platformio.ini`:

| Env | Purpose | Depends on |
|-----|---------|-----------|
| `Rook_companion_radio_usb`  | Companion radio over USB serial (for use with an external chat app) | `examples/companion_radio/` ✓ |
| `Rook_companion_radio_ble`  | Companion radio over BLE | `examples/companion_radio/` ✓ |
| `Rook_repeater`             | Standalone repeater node | `examples/simple_repeater/` ✓ |
| `Rook_sensor_broadcast`     | Broadcast environment telemetry | `examples/sensor_broadcast/main.cpp` *(missing — see note)* |
| `Rook_companion_sensor`     | Companion-app-paired sensor | `examples/companion_sensor/` ✓ (pulled in from MeshCore-simple-sensor) |

Four of the five envs build against the tree as-is. `Rook_sensor_broadcast` references `examples/sensor_broadcast/main.cpp`, which does not exist in upstream *or* in `edgecollective/MeshCore-simple-sensor` — the variant's `platformio.ini` needs either that file written, a pointer at an alternative main, or the env removed. Likely a leftover from an earlier name of the `simple_sensor` example.

### Build instructions (PlatformIO)

1. Install [PlatformIO](https://docs.platformio.org) — either the VS Code extension or the standalone `pio` CLI.
2. Clone this fork and enter it:
   ```bash
   git clone git@github.com:edgecollective/MeshCore-rook.git
   cd MeshCore-rook
   ```
3. List the envs PlatformIO has picked up (sanity check — the rook envs should be in the output):
   ```bash
   pio project config
   ```
4. Build one of the working envs (pick whichever fits your use):
   ```bash
   pio run -e Rook_companion_radio_usb
   pio run -e Rook_companion_radio_ble
   pio run -e Rook_repeater
   ```
5. Artifacts land under `.pio/build/<env-name>/`. The rook post-script (`variants/rook/create-uf2-post.py`) also emits a `.uf2` file suitable for drag-and-drop flashing via the Pro Micro nRF52840 USB bootloader.
6. Flash by uploading the `.uf2` to the USB mass-storage volume the board exposes when you double-tap its reset button. (Or use `pio run -e <env> -t upload` if you have the appropriate upload tooling configured.)

### Building on aarch64 (Raspberry Pi)

PlatformIO's prebuilt `toolchain-gccarmnoneeabi` package is x86_64-only — `pio run` on a Pi fails with `UnknownPackageError: Could not find the package with 'platformio/toolchain-gccarmnoneeabi @ ...' requirements`. Workaround: install Debian's system ARM toolchain and stage a PlatformIO-compatible package manifest that symlinks its binaries.

1. Install the Debian ARM toolchain:
   ```bash
   sudo apt install -y gcc-arm-none-eabi
   ```
2. Stage a PIO-package dir that PIO will accept via `symlink://`:
   ```bash
   STAGING=~/.local/share/pio-aarch64/toolchain-gccarmnoneeabi
   mkdir -p "$STAGING/bin"
   for tool in /usr/bin/arm-none-eabi-*; do
     ln -sf "$tool" "$STAGING/bin/$(basename "$tool")"
   done
   cat > "$STAGING/package.json" <<'JSON'
   { "name": "toolchain-gccarmnoneeabi", "version": "1.70201.0",
     "description": "system-installed gcc-arm-none-eabi (Debian apt)" }
   JSON
   ```
3. Create `platformio.local.ini` at the repo root pointing each Rook env at the staged package. This file is gitignored upstream:
   ```ini
   [env:Rook_repeater]
   platform_packages =
     ${nrf52_base.platform_packages}
     platformio/toolchain-gccarmnoneeabi@symlink:///home/YOUR_USER/.local/share/pio-aarch64/toolchain-gccarmnoneeabi
   ; (repeat the block for Rook_companion_radio_usb, Rook_companion_radio_ble, Rook_companion_sensor)
   ```
4. If a previous `pio run` failed mid-install, PIO may have left a stale cache pointer at `~/.platformio/packages/toolchain-gccarmnoneeabi.pio-link` — delete it before retrying, or PIO will keep chasing the old (broken) symlink target:
   ```bash
   rm -f ~/.platformio/packages/toolchain-gccarmnoneeabi.pio-link
   ```
5. `pio run -e Rook_repeater` should now proceed.

The Debian toolchain is GCC 14.2.1 (much newer than the GCC 6/7-era `toolchain-gccarmnoneeabi` that PIO's metadata nominally expects). One small patch was needed to compile under modern GCC: `src/helpers/sensors/RAK12035_SoilMoisture.cpp` gained an explicit `#include <ctime>` for `time_t`. The patch is included on this branch.

### First time? Double-check the LoRa region

`variants/rook/platformio.ini` inherits region-independent defaults from `nrf52_base`. Region frequency/BW overrides can be set per-env in `build_flags` (`-D LORA_FREQ=...`, `-D LORA_BW=...`, `-D LORA_SF=...`) — see `Rook_companion_sensor` for an example of overriding the radio params.

## ⚡️ MeshCore Flasher

We have prebuilt firmware ready to flash on supported devices.

- Launch https://meshcore.io/flasher
- Select a supported device
- Flash one of the firmware types:
  - Companion, Repeater or Room Server
- Once flashing is complete, you can connect with one of the MeshCore clients below.

## 📱 MeshCore Clients

**Companion Firmware**

The companion firmware can be connected to via BLE, USB or WiFi depending on the firmware type you flashed.

- Web: https://app.meshcore.nz
- Android: https://play.google.com/store/apps/details?id=com.liamcottle.meshcore.android
- iOS: https://apps.apple.com/us/app/meshcore/id6742354151?platform=iphone
- NodeJS: https://github.com/liamcottle/meshcore.js
- Python: https://github.com/fdlamotte/meshcore-cli

**Repeater and Room Server Firmware**

The repeater and room server firmwares can be setup via USB in the web config tool.

- https://config.meshcore.io

They can also be managed via LoRa in the mobile app by using the Remote Management feature.

## 🛠 Hardware Compatibility

MeshCore is designed for devices listed in the [MeshCore Flasher](https://meshcore.io/flasher)

## 📜 License

MeshCore is open-source software released under the MIT License. You are free to use, modify, and distribute it for personal and commercial projects.

## Contributing

Please submit PR's using 'dev' as the base branch!
For minor changes just submit your PR and we'll try to review it, but for anything more 'impactful' please open an Issue first and start a discussion. Is better to sound out what it is you want to achieve first, and try to come to a consensus on what the best approach is, especially when it impacts the structure or architecture of this codebase.

Here are some general principals you should try to adhere to:
* Keep it simple. Please, don't think like a high-level lang programmer. Think embedded, and keep code concise, without any unnecessary layers.
* No dynamic memory allocation, except during setup/begin functions.
* Use the same brace and indenting style that's in the core source modules. (A .clang-format is prob going to be added soon, but please do NOT retroactively re-format existing code. This just creates unnecessary diffs that make finding problems harder)

Help us prioritize! Please react with thumbs-up to issues/PRs you care about most. We look at reaction counts when planning work.

## Road-Map / To-Do

There are a number of fairly major features in the pipeline, with no particular time-frames attached yet. In very rough chronological order:
- [X] Companion radio: UI redesign
- [X] Repeater + Room Server: add ACL's (like Sensor Node has)
- [X] Standardise Bridge mode for repeaters
- [ ] Repeater/Bridge: Standardise the Transport Codes for zoning/filtering
- [X] Core + Repeater: enhanced zero-hop neighbour discovery
- [ ] Core: round-trip manual path support
- [ ] Companion + Apps: support for multiple sub-meshes (and 'off-grid' client repeat mode)
- [ ] Core + Apps: support for LZW message compression
- [ ] Core: dynamic CR (Coding Rate) for weak vs strong hops
- [ ] Core: new framework for hosting multiple virtual nodes on one physical device
- [ ] V2 protocol spec: discussion and consensus around V2 packet protocol, including path hashes, new encryption specs, etc

## 📞 Get Support

- Report bugs and request features on the [GitHub Issues](https://github.com/ripplebiz/MeshCore/issues) page.
- Find additional guides and components on [my site](https://buymeacoffee.com/ripplebiz).
- Join [MeshCore Discord](https://discord.gg/BMwCtwHj5V) to chat with the developers and get help from the community.
