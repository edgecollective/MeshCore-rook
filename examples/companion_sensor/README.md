# Companion Sensor

A MeshCore firmware example that reads a DS18B20 1-wire temperature sensor on a Heltec V3 and periodically sends readings as direct messages to a specific contact over the mesh network.

Messages use a `[SENSOR]` preamble to distinguish them from regular chat, making them easy to parse on the receiving end.

## Hardware Setup

### Components
- Heltec WiFi LoRa 32 V3
- DS18B20 temperature sensor (optional -- firmware uses a dummy value if no sensor is detected)
- 4.7k ohm pullup resistor

### Wiring (Heltec V3)

```
DS18B20        Heltec V3
-------        ---------
VCC (red)  --> 3.3V
GND (black) -> GND
DATA (yellow) -> GPIO 7
```

### Wiring (Rook)

```
DS18B20        Rook
-------        ----
VCC (red)  --> 3.3V
GND (black) -> GND
DATA (yellow) -> P1.06 (Arduino pin 9)
```

Place a 4.7k ohm resistor between the DATA line and 3.3V (pullup).

The data pin is configurable via the `-D ONEWIRE_PIN=N` build flag.

## Building and Flashing

### Heltec V3

```bash
pio run -e Heltec_v3_companion_sensor -t upload
```

### Rook (nRF52840)

```bash
# Build
pio run -e Rook_companion_sensor

# Flash via UF2: double-tap reset, then copy
cp .pio/build/Rook_companion_sensor/firmware.uf2 /media/$USER/*/

# Or flash via PlatformIO
pio run -e Rook_companion_sensor -t upload
```

The Rook uses pin P1.06 (Arduino pin 9) for the DS18B20 data line.

### Serial Monitor

```bash
pio device monitor -b 115200
```

**Tip:** Use `pio device monitor` instead of `screen` — it automatically releases the serial port when you need to upload new firmware.

## Setup Workflow

### Step 1: Flash and Boot Both Nodes

You need two nodes: the **sensor node** (running this firmware) and a **receiving node** (e.g. a companion radio running the MeshCore app, or another Heltec running `simple_secure_chat`).

Flash the sensor firmware. On first boot, press ENTER in the serial monitor to generate a cryptographic identity.

Optionally, give the sensor node a name (default is "Sensor"):

```
set name MyTempSensor
```

This name is what other nodes will see in advertisements and contact lists. It's saved to flash and persists across reboots.

### Step 2: Make Sure Both Nodes Use the Same Radio Settings

Both nodes must be on the same frequency, bandwidth, spreading factor, and coding rate. The default settings for this firmware are:

| Parameter | Value |
|-----------|-------|
| Frequency | 910.525 MHz |
| Bandwidth | 62.5 kHz |
| Spreading Factor | 7 |
| Coding Rate | 5 |

If the receiving node is a **companion radio**, set its radio params with meshcli:

```bash
meshcli -s /dev/ttyUSB0 set radio 910.525,62.5,7,5
meshcli -s /dev/ttyUSB0 reboot
```

### Step 3: Exchange Contacts

Both nodes need each other's contact cards for encrypted messaging to work. The exchange must go **both ways**.

The procedure depends on what type of node the receiver is:

---

#### Receiver is a Companion Radio (meshcli)

**Get the companion radio's card:**

```bash
meshcli -s /dev/ttyACM0 card
```

This prints a `meshcore://...` hex string. Copy it.

**Import the companion radio's card into the sensor node** (sensor serial monitor):

```
import meshcore://PASTE_HEX_HERE
```

**Get the sensor node's card** (sensor serial monitor):

```
card
```

This prints a `meshcore://...` hex string. Copy it.

**Import the sensor's card into the companion radio:**

```bash
meshcli -s /dev/ttyACM0 import_contact "meshcore://PASTE_HEX_HERE"
```

---

#### Receiver is Another Serial Node (simple_secure_chat, another companion_sensor, etc.)

**On the sensor node** (serial monitor):

```
card
```

Copy the `meshcore://...` output.

**On the receiving node** (its serial monitor):

```
import meshcore://PASTE_HEX_HERE
```

**On the receiving node:**

```
card
```

Copy its `meshcore://...` output.

**Back on the sensor node:**

```
import meshcore://PASTE_HEX_HERE
```

---

#### Via Over-the-Air Advertisements

If both nodes are within radio range and using the same radio settings, they will automatically discover each other via mesh advertisements. You'll see:

```
ADVERT from -> NodeName
```

This auto-saves the contact. However, this only works one direction at a time — both nodes need to hear each other's advertisement. You can force an advertisement from the sensor with:

```
advert
```

Or long-press the button on the "Send Advert" display page.

**Note:** Advertisement-based discovery only shares public keys and names. It works for sending messages, but the receiving node also needs the sensor's contact to decrypt incoming messages.

---

#### Using contact_exchange.py (Both Nodes on USB)

If both nodes are companion radios connected via USB simultaneously:

```bash
cd examples/companion_radio/contact_exchange
python contact_exchange.py exchange /dev/ttyUSB0 /dev/ttyACM0
```

**Note:** This script uses the companion radio binary protocol, so it only works if both nodes are running companion radio firmware. It won't work with the sensor node's text-based serial interface.

### Step 4: Set the Target Contacts

Tell the sensor which contact(s) should receive the readings. The sensor supports up to **4 targets**, which is useful for range testing (one stationary receiver plus a mobile one, for example).

**Single target:**
```
target ReceiverName
```

**Multiple targets:**
```
target add HomeReceiver
target add MobileReceiver
target add BackupReceiver
```

Name matching is prefix-based, so `target add Home` works if the name is unique. Verify the current target list with:

```
target
```

To remove or reset:
```
target remove HomeReceiver
target clear
```

Targets are saved to flash and persist across reboots. When `send` is triggered (manually or on interval), the sensor sends the reading to all targets in sequence.

You can see all known contacts with:

```
list
```

### Step 5: Verify

The sensor will now automatically send temperature readings every 5 minutes (default). To test immediately:

```
send
```

Or long-press the button on the "Send Sensor" display page.

You should see on the sensor serial monitor:

```
   [SENSOR] [SENSOR] node_id=1 temp=22.50C batt=3.85V
   -> ReceiverName: sent (FLOOD)
   (1/1 sent)
   Got ACK! (round trip: 1234 millis)
```

And the message should appear on the receiving node.

## Display and Button

The OLED display has 3 pages, cycled with a **short press** of the user button:

| Page | Shows | Long Press Action |
|------|-------|-------------------|
| **Status** | Temperature, battery, target, interval | — |
| **Send Sensor** | "long press" prompt | Sends a sensor reading now |
| **Send Advert** | "long press" prompt | Broadcasts a mesh advertisement |

The display turns off after 30 seconds of inactivity. Any button press wakes it.

## Message Format

```
[SENSOR] node_id=1 temp=22.50C batt=3.85V
```

- `[SENSOR]` prefix identifies sensor data messages
- `node_id=` numeric node identifier (default 1, configurable via `set node_id`)
- `temp=` temperature in Celsius from DS18B20 (or 99.9 if no sensor)
- `batt=` battery voltage in volts

## Serial Commands

| Command | Description |
|---------|-------------|
| `card` | Show your biz card for sharing |
| `import <biz card>` | Import a contact's biz card |
| `list {n}` | List contacts (optionally last n); shows `Contacts: N/MAX` header |
| `purge` | Clear all stored contacts |
| `target` | Show current targets |
| `target add <name>` | Add a send target (max 4) |
| `target remove <name>` | Remove a send target |
| `target clear` | Clear all targets |
| `target <name>` | Set to a single target (replaces any existing) |
| `to <name>` | Alias for `target <name>` |
| `send` | Send a reading immediately |
| `set name <name>` | Set the node's advertised name |
| `set node_id <id>` | Set node ID (1-65535, default 1) |
| `set interval <secs>` | Set send interval in seconds (min 10) |
| `advert` | Send a mesh advertisement |
| `ver` | Show firmware version |
| `help` | Show command help |

## Build Flags

| Flag | Default | Description |
|------|---------|-------------|
| `ONEWIRE_PIN` | 7 | GPIO pin for DS18B20 data line |
| `ADVERT_NAME` | "Sensor" | Node name advertised on the mesh (runtime: `set name`) |
| `SENSOR_SEND_INTERVAL_SECS` | 300 | Send interval in seconds (5 min) |
| `MAX_CONTACTS` | 32 | Maximum number of stored contacts |
| `LORA_FREQ` | 910.525 | LoRa frequency in MHz |
| `LORA_BW` | 62.5 | LoRa bandwidth in kHz |
| `LORA_SF` | 7 | LoRa spreading factor |
| `LORA_CR` | 5 | LoRa coding rate |

## Dummy Mode

If no DS18B20 sensor is detected at boot, the firmware runs in dummy mode:
- Temperature is reported as `99.9C`
- All other functionality (mesh, contacts, sending) works normally
- Useful for development and testing without sensor hardware
