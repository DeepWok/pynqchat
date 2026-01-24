# Lab 2: Audio Processing

## 2.1 Introduction

In this lab, we will utilize the microphone input and audio output on the PYNQ-Z1 board and set up audio processing capabilities for future sections. We begin by exploring the Base Overlay design provided by the PYNQ team.

According to the PYNQ documentation:

> "The purpose of the base overlay design is to allow PYNQ to use peripherals on a board out-of-the-box. The design includes hardware IP to control peripherals on the target board, and connects these IP blocks to the Zynq PS. If a base overlay is available for a board, peripherals can be used from the Python environment immediately after the system boots."

> For further information, please read: <https://pynq.readthedocs.io/en/latest/pynq_overlays/pynqz1/pynqz1_base_overlay.html>

## 2.2 Audio Processing (Software)

In this section, we will learn how to utilize the BaseOverlay and implement basic audio processing in software.

To make a Whisper API call, we need to send audio in a format accepted by the Whisper API. The PYNQ-Z1 board's onboard microphone is a MEMS (Micro-Electro-Mechanical Systems) microphone that records in PDM (Pulse Density Modulation) format.

A brief overview of the format types:

| Format | Use Case | Description |
|--------|----------|-------------|
| **PDM** (Pulse Density Modulation) | Recording | MEMS microphones use PDM because it offers a straightforward, noise-immune digital output that is compact and cost-effective. |
| **PCM** (Pulse Code Modulation) | Storage | PCM is the standard for digital audio because it aligns well with digital processing, maintains audio quality, and serves as the basis for compression formats. |
| **PWM** (Pulse Width Modulation) | Playback | PWM is used for audio playback because it efficiently drives output devices, simplifies DAC implementation, and is power-efficient. |

Explore the characteristics and details of these different formats; you should find familiar concepts from your Signals and Systems and Communications modules.

The BaseOverlay provides PDM-to-PWM conversions to enable playback from the audio buffer. However, to utilize Whisper, we need to convert the recorded PDM data into PCM, which can then be wrapped in a standard audio file format such as `.wav` or `.mp3` before making an API call.

Let's begin by examining a software PDM-to-PCM conversion function in Python.

### Task 2A: Software PDM-to-PCM Conversion Function

> **Note:** For this task, you don't need to write any code—just download, run, and experiment with the [audio playback notebook](https://github.com/Xilinx/PYNQ/blob/master/boards/Pynq-Z1/base/notebooks/audio/audio_playback.ipynb).

The PYNQ-Z1 board's BaseOverlay enables you to easily record and play back audio using the onboard MEMS microphone and audio output. The software interface allows you to record, save, and play audio using simple Python functions.

You can adjust recording time and playback volume, and visualize or process recordings directly in Python.

**Your Task:** Download and run the `audio_playback.ipynb` Jupyter notebook (provided by PYNQ) to experiment with recording and playing back audio on your board.

As you will see, the BaseOverlay design (and its bitfile `base.bit`) is already included in the PYNQ files, so the notebook simply imports it from `pynq.overlays.base`.

## 2.3 Audio Processing (Hardware)

In this section, you will understand how PYNQ acts as an "embedded Python wrapper" that allows you to interact with your block design's components. We will take an embedded systems approach to modify the BaseOverlay and learn how drivers interact with hardware components. The goal is to create a hardware-based solution for the PDM-to-PCM conversion we just completed in software.

First, we need to examine the audio components in the BaseOverlay's block design. To do this, we must download and open the design from Xilinx's PYNQ repository.

**Steps:**

1. Clone the PYNQ repository and check out release version v2.7.0:
2. Navigate to `boards/Pynq-Z1/base`, where you will find the `base.tcl` and `build_ip.tcl` scripts.

```bash
git clone https://github.com/Xilinx/PYNQ.git
cd PYNQ
git checkout v2.7.0
cd boards/Pynq-Z1/base
ls  # You will see base.tcl and build_ip.tcl
```

3. Open the Vivado GUI starting page. You will see a Tcl console at the bottom of the window.
4. In the console, navigate to the directory and source both files. For example:

```tcl
cd W:/PYNQ-master/boards/Pynq-Z1/base  # Navigate to your PYNQ directory
source build_ip.tcl
source base.tcl
```

> **Debug:** It has been noticed that several groups have run into issues with `source base.tcl` failing. This is because `build_ip.tcl` is not generating the HLS IPs and saving it to the correct directory properly. This is due to an overflow bug by Vivado. Refer to this general [solution](../debug.md#vivado-y2k22) to the bug.

> **Note:** If you need help launching the `.tcl` script from the terminal or Vivado GUI, refer to these [instructions](https://xilinx.github.io/Alveo-Cards/cards/ul3524/build/html/docs/Docs/loading_ref_proj.html).

![](/images/lab2-source-tcl.jpg)

Since the BaseOverlay connects to every peripheral on the PYNQ board, the design is quite large. Expect `source base.tcl` to take approximately 10 minutes to complete.

Once the block design is built, let's begin by **understanding** the audio module in the BaseOverlay (you don't need to edit it yet). Open the block design and zoom to the bottom-right corner to find the `audio_direct_v1_1` module. What does it do? How does it interact with the board? Let's explore.

**Exploring the Audio Module:**

1. Search for the `audio_direct` module in the "Sources" window.

![](/images/lab2-audio-direct-module.jpg)

2. Double-click on `base_audio_direct_0_0` and select "Edit in IP Packager".

![](/images/lab2-edit-in-ip-packager.jpg)

This will open a new Vivado window that displays the design source files within the `audio_direct_v1_1` IP. Open the file hierarchy under "Design Sources" to find:

![](/images/lab2-audio-direct-hierarchy.jpg)

**Understanding the Hierarchy:**

The audio module's internal hierarchy shows that under the `base_audio_direct_0_0` IP, there is an `audio_direct_v1_1.v` file. This is the actual IP developed by the PYNQ/Digilent teams, while `base_audio_direct_0_0` is auto-generated when you add your IP to the block design and interface it with other components.

Under the `audio_direct_v1_1` IP, we see two sub-hierarchies:

- `d_axi_pdm_v1_2_S_AXI.vhd`
- `audio_direct_path.sv`

By examining the HDL code and Python driver [`audio.py`](https://github.com/Xilinx/PYNQ/blob/master/pynq/lib/audio.py), you'll discover that `audio_direct_path` enables an audio bypass where the PDM microphone input is directly streamed to the PWM output.

But recall from section 2.1 that you could also record to an audio buffer and save the audio data. How is this buffer built?

**The FIFO Buffer:**

The `d_axi_pdm_v1_2_S_AXI` module provides this functionality. While the VHDL may seem complex, it essentially instantiates a FIFO that can be controlled through register offsets in the drivers. This is done by instantiating an AXI4 Peripheral, similar to the method we used in Lab 1 Task 1.3.

Just as we wrote our own merge array drivers, PYNQ has written [C++ audio drivers](https://github.com/Xilinx/PYNQ/blob/master/pynq/lib/_pynq/_audio/audio_direct.cpp#L59) that write values to these register offsets to control the FIFO's behavior. You can match the register offsets in the VHDL file with the audio controller registers in the [C++ audio driver header file](https://github.com/Xilinx/PYNQ/blob/master/pynq/lib/_pynq/_audio/audio_direct.h).

**Python-C++ Integration:**

How does the Python audio driver use the C++ functions? Remember CFFI from Lab 1? The low-level C++ operations are compiled into a shared library file `libaudio.so`, which Python then loads:

```python
self._libaudio = self._ffi.dlopen(LIB_SEARCH_PATH + "/libaudio.so")
```

which is compiled from the C++ audio drivers using CMake.

**Important:** Save the IP editing project for `audio_direct_v1_1` in a location you can easily find—you will need these files in a later task.

**Working with a Simplified Design:**

Since the BaseOverlay is large and time-consuming to synthesize and implement, a simplified version has been provided. Source the `bd/lab2-skeleton/lab2-skeleton.tcl` script to open the skeleton design. You will see the following incomplete block design:

![](/images/lab2-skeleton-design.jpg)

**Objective:**

The goal of this hardware section is to create a block design that performs PDM-to-PCM conversion by building upon the BaseOverlay's audio infrastructure.

Here is what the final design should look like:

![](/images/lab2-end-goal-design.jpg)

Now let's begin the hardware implementation!

### Task 2B: Creating an Audio Frontend (PDM-to-PCM Converter)

We need a hardware module that mirrors the PDM-to-PCM functions written in Python. We will use Xilinx's CIC Compiler IP, specifically its decimation filter.

**Background:**

Decimation reduces the sampling rate by retaining only every Nth sample while applying anti-aliasing filtering. CIC (Cascaded Integrator-Comb) filters are ideal for PDM-to-PCM conversion because they efficiently decimate high-frequency PDM bitstreams (often several MHz) down to standard audio sampling rates (e.g., 44.1 kHz) without requiring multipliers.

**Useful References:**

- [Moving Average and CIC Filters](https://tomverbeure.github.io/2020/09/30/Moving-Average-and-CIC-Filters.html)
- [CIC Filters Explained (YouTube)](https://www.youtube.com/watch?v=8RbUSaZ9RGY)
- [CIC Compiler Documentation - AMD](https://docs.amd.com/v/u/en-US/pg140-cic-compiler)

**Implementation Steps:**

1. Create a new Vivado project with the same target board. This time, don't create a block design initially.
2. Click the "+" button under the "Sources" window.
3. Select "Add or create design sources", then "Create File".
4. The file type should default to "Verilog". Name the file "pdm_mic" (or another descriptive name).

5. Copy and paste the completed `pdm_mic.v` from the `hw_files` directory in this repository.
6. You will see two question marks under `pdm_microphone` in the Design Sources hierarchy: `pdm_clk_gen` and `cic_compiler`.

![](/images/lab2-pdm-mic-sources.jpg)

7. Repeat the file creation procedure for `pdm_clk_gen`.
8. For `cic_compiler`, click on "IP Catalog" in the sidebar under "Project Manager".

![](/images/lab2-cic-ip-catalog.jpg)

9. Configure the CIC Compiler as shown below:

![](/images/lab2-cic-config-1.jpg)
![](/images/lab2-cic-config-2.jpg)

10. The final design should look like this:

![](/images/lab2-audio-frontend.jpg)

> **Reference:** If you need additional guidance, refer to this [article on CIC compiler PDM-to-PCM decimation](https://community.element14.com/challenges-projects/design-challenges/pathprogrammable3/b/blog/posts/p2p3-amd-vivado-cascaded-integrator-comb-cic-compiler-pdm-microphone-to-pcm-decimation).

**Packaging the IP:**

11. Select **Tools > Create and Package New IP**. You will see the following options:

![](/images/lab2-package-ip.jpg)

12. Select "Package your current project" and click through the default settings.
13. Complete the packaging process:

![](/images/lab2-package-ip-interface.jpg)

### Task 2C: Modifying the audio_direct IP to Work with PCM Data

Now that we have a frontend module that converts incoming PDM data to PCM data, we need to modify the `audio_direct` module to handle PCM data instead of PDM data.

**Understanding the Modification:**

The BaseOverlay's `audio_direct` module uses an AXI4 peripheral controlled by MMIO registers.

Since we're converting the PDM input from the microphone to PCM, we must modify the RX (receive) FIFO to accept 32-bit inputs instead of 1-bit inputs. PCM uses 32-bits while PDM uses 1-bit in the current design. At this stage, we won't modify the Tx (transmit) side.

> The Tx-side "serializer" expects 16-bit inputs from the Tx FIFO and outputs 1-bit outputs for PWM playback. Hence, you should generate one 32-bit wide FIFO and one 16-bit wide FIFO. The image below is an older screenshot which incorrectly shows both the Tx-side FIFO and the Rx-side FIFO using the same generated IP.

![](/images/lab2-audio-direct-modified.jpg)

The figure above shows the target `audio_direct_v1_1` hierarchy. We will replace the old VHDL AXI4 peripheral file (`audio_direct_v1_1_S_AXI_inst`) with a newer Verilog version.

**Available Files:**

The Verilog counterparts of the components are available in the `hw_files` directory:

- [`audio_direct_v1_1_S00_AXI.v`](/hw_files/audio_direct_v1_1_S00_AXI.v)
- [`audio_direct_v1_1.v`](/hw_files/audio_direct_v1_1.v)
- [`pdm_clk_gen.v`](/hw_files/pdm_clk_gen.v)
- [`pdm_mic.v`](/hw_files/pdm_mic.v)
- [`pdm_rxtx.v`](/hw_files/pdm_rxtx.v)
- [`pdm_ser.v`](/hw_files/pdm_ser.v)

**Your Task:**

Compare the new hierarchy with the old hierarchy. Which files were removed? Which files need modification?

Using your experience from exploring the BaseOverlay, modify the old `audio_direct` hierarchy to support PCM.

**Hint:** Start with the design source files within the `audio_direct_v1_1` IP that you explored earlier in this section.

**Hint:** You may need to instantiate new IPs based on what you see is missing there when instantiating your own `audio_direct_v1_1`.

Once finished, package the IP.

### Task 2D: Connecting the Modified Modules

Now let's connect the audio frontend created in Task 2B with the modified `audio_direct` IP developed in Task 2C.

**Adding the Custom IPs:**

1. Starting from the `lab2-skeleton` design, add the two IPs built in Tasks 2B and 2C.
2. First, ensure the skeleton Vivado project can locate your packaged IPs:
   - Click **Settings** in the sidebar (Project Manager)
   - Navigate to **IP > Repository**
   - Add the path where you saved your IP projects
   - **Tip:** If you saved all Vivado projects in the same directory (e.g., `vivado_ws`), add that top-level directory, and Vivado will auto-detect all IPs within it.

![](/images/lab2-add-ip-repository.jpg)

3. Add the IPs to the block design and connect them as shown:

![](/images/lab2-final-design.jpg)

**Creating Ports:**

4. Create the following input/output ports by right-clicking on the block diagram and selecting "Create Port":

   - `pdm_m_data_i` (input)
   - `pwm_audio_o[0:0]` (output, vector of size 1)
   - `pdm_audio_shutdown[0:0]` (output, vector of size 1)
   - `pdm_m_clk[0:0]` (output, vector of size 1)

> **Note:** These port names must match the constraint file.

![](/images/lab2-create-port.png)

**Adding Constraints:**

5. Set the proper constraints for the newly created ports. Reuse constraints from the BaseOverlay design: [base.xdc](https://github.com/Xilinx/PYNQ/blob/image_v2.7/boards/Pynq-Z1/base/vivado/constraints/base.xdc).
   - Click the "+" button under the "Sources" window
   - Select "Add or create constraints"
   - Select "Add Files" and navigate to the `base.xdc` file

**Generating the Bitstream:**

6. Generate the bitstream and obtain the required `tcl`, `hwh`, and `bit` files (repeat the steps from Lab 1).

> **Tip:** Run "Validate Design" before bitstream generation to check for errors. [Reference](https://docs.amd.com/r/en-US/ug995-vivado-ip-subsystems-tutorial/Step-8-Validating-the-Design)

### Task 2E: Understanding and Modifying the Drivers

> **Note:** In this task, you don't need to write any code—the goal is to understand how the drivers work.

We need a new Python driver to work with PCM data instead of PDM data. The concepts are similar to the array merging drivers from Lab 1.

A modified Python driver file is provided at [drivers/pcm_driver/new_audio.py](drivers/pcm_driver/new_audio.py), which you can use to replace the original `audio.py` on your PYNQ board.

> **For detailed instructions, read:** [drivers/pcm_driver/driver_instructions.md](/drivers/pcm_driver/driver_instructions.md)

**Understanding the Driver Architecture:**

Before copying the new `audio.py`, let's understand how the drivers work. A test/debug C++ driver was created for PCM (not present in the original PYNQ codebase). Compare it with the [original PYNQ C++ driver](https://github.com/Xilinx/PYNQ/blob/master/pynq/lib/_pynq/_audio/audio_direct.cpp).

**How the C++ Driver Works:**

1. **Register Definitions:** Register offsets relative to the AXI4 peripheral's base address are defined as constants, along with transmit and receive FIFO flags.
2. **Access Functions:** Two inline functions, `Read32` and `Write32`, enable reading from and writing to these registers to control the AXI4 peripheral.
3. **Driver Functions:** Functions like `record` control the AXI4 peripheral to record and save receive FIFO data into a statically-allocated buffer.

The C++ drivers in the PYNQ codebase (under `pynq/lib/_pynq/_audio`) work similarly, except they rely on a buffer created in the `audio.py` Python driver rather than creating a static buffer in C++.

**Examining the Python Driver:**

Now examine [drivers/pcm_driver/new_audio.py](/drivers/pcm_driver/new_audio.py). Functions are marked as either `not changed` or `changed` compared to PYNQ's original Python driver for easy comparison.

As you learned from the merge array example in Lab 1, the Makefile compiles the C++ drivers into a `libaudio.so` shared library, which Python loads using CFFI (C Foreign Function Interface). The main changes are in the `record` and `save` functions, where the expected buffer data sampling rate and audio file type have been modified.

> **Important:** Do not use the C++ files or Makefile in the `pcm_driver` folder. Follow the instructions in the markdown file and only use `new_audio.py`.

### Task 2F: Testing the Drivers in Jupyter Notebook

After following the driver instructions, let's test the implementation in Jupyter Notebook.

**Testing Steps:**

1. Upload the `lab2-hw.ipynb` notebook from `jupyter_notebook/lab2` to your PYNQ board (similar to Lab 1).
2. Run all cells. This should record and save a file named `rec1.wav`.
3. Download the file to your local device.
4. Play it using your OS's default audio player.
5. Verify that you can hear the full recorded audio.

> **Troubleshooting:** If you don't hear anything, use an ILA to debug your hardware design: [ILA Tutorial](https://www.youtube.com/watch?v=5-CR5MRGPJE)

## 2.4 Conclusion

Congratulations on completing Lab 2! You have gained hands-on experience with both software and hardware audio processing on the PYNQ-Z1 board.

**What You Accomplished:**

- Explored the PYNQ BaseOverlay and its audio components
- Implemented software-based PDM-to-PCM conversion
- Created a hardware-based PDM-to-PCM converter using CIC filters
- Modified IP modules to handle PCM data
- Integrated custom IPs into a block design
- Understood the interaction between Python and C++ drivers using CFFI

**Looking Ahead:**

This foundation in audio processing and hardware-software co-design is essential for upcoming sections where you'll integrate speech recognition capabilities using the Whisper API. You now have a complete audio pipeline that can capture microphone input, convert it to standard PCM format in hardware, and save it as WAV files ready for further processing.
