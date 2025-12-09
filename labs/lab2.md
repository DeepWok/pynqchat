# Lab 2: Audio Processing

## 2.1 Introduction

In this section, we will utilise the microphone input and audio output on the PYNQ-Z1 board, and setup audio processing capabilities for future sections. We first explore the Base Overlay design provided by the PYNQ team.

Quoting the PYNQ documentation:
"The purpose of the base overlay design is to allow PYNQ to use peripherals on a board out-of-the-box. The design includes hardware IP to control peripherals on the target board, and connects these IP blocks to the Zynq PS. If a base overlay is available for a board, peripherals can be used from the Python environment immediately after the system boots"

> For further information, please read: <https://pynq.readthedocs.io/en/latest/pynq_overlays/pynqz1/pynqz1_base_overlay.html>

## 2.2 Audio Processing (Software)

In this section, we will learn how to utilise the BaseOverlay and implement some basic audio processing in software.

In order to make a Whisper API call, we need to send the audio in a format that is accepted by Whisper. Unfortunately, the PYNQ-Z1 board's onboard microphone is a MEMS (Micro-Electro-Mechanical Systems) microphone, which records in PDM (pulse density modulation) format.

A brief overview of the format types:

| Format | Use Case | Description |
|--------|----------|-------------|
| **PDM** (Pulse Density Modulation) | Recording | MEMS microphones use PDM because it offers a straightforward, noise-immune digital output that is compact and cost-effective. |
| **PCM** (Pulse Code Modulation) | Storage | PCM is the standard for digital audio because it aligns well with digital processing, maintains audio quality, and serves as the basis for compression formats. |
| **PWM** (Pulse Width Modulation) | Playback | PWM is used for audio playback because it efficiently drives output devices, simplifies DAC implementation, and is power-efficient. |

Please go ahead and explore the characteristics and details of these different formats, where you should find familiar information related to your Signals and Systems / Communications modules.

The BaseOverlay provides you with PDM to PWM conversions to allow for playback from the audio buffer, as demonstrated in section 2.1. But to utilise Whisper, we need to convert the recorded PDM files into PCM, which can then be wrapped as a common audio file format such as `.wav` or `.mp3`, before making an API call.

Let's start by looking at a software PDM-PCM conversion function in Python.

### Task 2A: Software PDM-PCM conversion function

The PYNQ-Z1 board's BaseOverlay lets you easily record and play back audio using the onboard MEMS microphone and audio output. The software controls allow you to record, save, and play audio using simple Python functions.

You can adjust recording time and playback volume, and visualize or process recordings directly in Python.

Try it yourself - Download the [audio_playback.ipynb](https://github.com/Xilinx/PYNQ/blob/master/boards/Pynq-Z1/base/notebooks/audio/audio_playback.ipynb) Jupyter notebook from PYNQ repo, upload it to your board, and run the notebook experiment with recording and playing back audio.

As you will see, the BaseOverlay design (and its bitfile `base.bit`) is already included in the PYNQ files, so the notebook simply imports it from `pynq.overlays.base`.

## 2.3 Audio Processing (Hardware)

In this section you will get to understand how exactly the PYNQ acts as a "embedded Python wrapper" which allows you to interact with your block design's components. Here we will take more of a embedded systems approach and modify both the BaseOverlay and also learn how drivers interact with those components. The end goal is to create a hardware-based solution for the PDM-to-PCM conversion we just completed in software.

We now want to observe the audio components in the BaseOverlay's block design. To do so, we first need to download and open the design from Xilinx's PYNQ repository. Go to: <https://github.com/Xilinx/PYNQ/tree/master>, and git clone the PYNQ repository locally. Based on the Vivado version installed, select the corresponding release version image.

![](/images/versions.png)

For example, if you are using Vivado 2020.2, you would checkout the tag `v2.7.0` :

```bash
git clone https://github.com/Xilinx/PYNQ.git
cd PYNQ
git checkout v2.7.0
```

> Reference: <https://pynq.readthedocs.io/en/latest/pynq_sd_card.html3>

Under the PYNQ repository which you downloaded, navigate to `boards/Pynq-Z1/base`. You will find a `base.tcl` and `build_ip.tcl` script.

Now open up the Vivado GUI starting page. You will see a Tcl console at the bottom of window. In the console, navigate to the directory above and source both files. For example:

```tcl
cd E:/PYNQ/boards/Pynq-Z1/base # Navigate to your local path
source build_ip.tcl
source base.tcl
```

> If you still don't know how to launch the .tcl script from terminal or Vivado gui, reference the instructions in this link: <https://xilinx.github.io/Alveo-Cards/cards/ul3524/build/html/docs/Docs/loading_ref_proj.html>

![](/images/source.jpg)

As the BaseOverlay connects to every single peripheral on the PYNQ board, the design is quite large compared to some of your smaller hobbyist designs, so waiting for `source base.tcl` to finish running will take some time (~10 minutes).

Once the block design is built, let's start by understanding the audio module in the BaseOverlay. Open up the block design and zoom to the bottom right corner, there you will find the `audio_direct_v1_1` module. What does it do? How does it interact with the board exactly? Let's explore.

Search for the module `audio_direct` in the "Sources" window.

![](/images/audio_direct.jpg)

Double click on the `base_audio_direct_0_0` and press `Edit in IP Packager`.

![](/images/editinip.jpg)

That will open up a new Vivado window which allows us to see the design source files within the `audio_direct_v1_1` ip. If we open up the hierarchy of files under "Design Sources", we will find:

![](/images/audio_direct_layers.jpg)

Here we see the audio module's internal hierarchy - under the `base_audio_direct_0_0` IP, there is a `audio_direct_v1_1.v` file. The `audio_direct_v1_1.v` is the actual IP that was developed by the PYNQ / Digilent teams, while the `base_audio_direct_0_0` is auto-generated when you add your IP to your block design and interface it with other components.

Under the `audio_direct_v1_1` IP, we see two different hierarchies - one named the `d_axi_pdm_v1_2_S_AXI.vhd`, the other named `audio_direct_path.sv`. By looking at the HDL code and Python driver [`audio.py`](https://github.com/Xilinx/PYNQ/blob/master/pynq/lib/audio.py), you would discover that `audio_direct_path` allows for an audio bypass, where the input to the PDM microphone is directly streamed to the PWM output.

But remember that in section 2.1, you were also able to record to an audio buffer and save the audio data from the buffer? How exactly is the buffer built?

That's where the `d_axi_pdm_v1_2_S_AXI` module comes in. The `vhdl` might seem confusing, but essentially it just instantiates a FIFO that can be controlled through certain register offsets in the drivers. This can be done by instantiating an `AXI4 Peripheral`, which is exactly the method we used in lab 1 task 1.3.

Similar to us writing our own merge array drivers, PYNQ has written [C++ audio drivers](https://github.com/Xilinx/PYNQ/blob/master/pynq/lib/_pynq/_audio/audio_direct.cpp#L59) which writes values to these register offsets to control the behaviour of the FIFO. You can match the register offsets in the `vhdl` file with the audio controller registers in the [header file of the C++ audio driver](https://github.com/Xilinx/PYNQ/blob/master/pynq/lib/_pynq/_audio/audio_direct.h).

So how does the Python audio driver use the C++ functions? Remember CFFI from lab 1? The low-level operations written in C++ above get compiled into a shared libary file `libaudio.so`. Python then loads this file:

```python
self._libaudio = self._ffi.dlopen(LIB_SEARCH_PATH + "/libaudio.so")
```

which is compiled from the C++ audio drivers using CMake.

Firstly, save the IP editing project for the `audio_direct_v1_1` in a filepath that you can find easily - you will need those files in a later task.

As the BaseOverlay is incredibly large, it takes quite some time for it to run synthesis and implementation. For convenience, I have provided a shrunk down version of the BaseOverlay as a tcl script under `bd/lab2/lab2-skeleton`. Source the script to open up a new design. You will see the following incompleted block design:

![](/images/skeleton.jpg)

Our final goal is of this hardware section is to create a block design that does the PDM-to-PCM conversion, by making changes on top of the BaseOverlay's audio infrastructure.

This is a picture of the end goal:

![](/images/end-goal.jpg)

Now let's do the hardware programming!

### Task 2B: Creating an audio frontend (PDM-to-PCM converter)

First, we need something in hardware which mirrors the PDM-to-PCM functions written in Python. Here we will use Xilinx's CIC Compiler IP, specifically its decimation filter.

Decimation reduces the sampling rate by keeping only every Nth sample while applying anti-aliasing filtering. CIC filters are ideal for this PDM-to-PCM conversion as they efficiently decimate the high-frequency PDM bitstream (often several MHz) down to standard audio sampling rates (e.g., 44.1 kHz) without requiring multipliers.

Useful references:

- [Moving Average and CIC Filters](https://tomverbeure.github.io/2020/09/30/Moving-Average-and-CIC-Filters.html)
- [CIC Filters Explained (YouTube)](https://www.youtube.com/watch?v=8RbUSaZ9RGY)
- [CIC Compiler Documentation - AMD](https://docs.amd.com/v/u/en-US/pg140-cic-compiler)

Start by creating a new Vivado project with the same target board. This time we don't create a block design. Click on the "+" ubnder the "Sources" window. Select "Add or create design sources", then "Create File". The file type should be defaulted to "Verilog", and name the file name "pdm_mic" (or whatever makes sense to you).

Copy and paste the already completed [`pdm_mic.v`](/hw_files/pdm_mic.v) under `hw_files` in this repository. You will see two question marks under `pdm_microphone` in Design Sources hierarchy - one of them is `pdm_clk_gen`, and the other is `cic_compiler`.

![](/images/pdm_mic.jpg)

Repeat the create file procedure above for `pdm_clk_gen` ([`pdm_clk_gen.v`](/hw_files/pdm_clk_gen.v)).

For the `cic_compiler`, click on "IP Catalog" on the sidebar under "Project Manager".

![](/images/cic.jpg)

The configurations should be:

![](/images/cic1.jpg)
![](/images/cic2.jpg)

And you should end up with:

![](/images/audio_frontend.jpg)

> If confused, take a look at this article: <https://community.element14.com/challenges-projects/design-challenges/pathprogrammable3/b/blog/posts/p2p3-amd-vivado-cascaded-integrator-comb-cic-compiler-pdm-microphone-to-pcm-decimation>

Now we have to package the IP. In case you have forgotten, select "Tools > Create and Package New IP", which will give you the following options:

![](/images/package_ip.jpg)

Select "Package your current project", and click through the default settings.

Then package your IP:

![](/images/package_ip_if.jpg)

### Task 2C: Modifying the audio_direct ip to work with PCM data

> 📝 For this task, you need to create a new ip based on `audio_direct_v1_1`.

Now we have some frontend module which converts the incoming PDM data into PCM data, we need to modify the `audio_direct` module to be able to handle PCM data instead of PDM data.

As we know, under the hood of the BaseOverlay's `audio_direct` is an AXI4 peripheral which are MMIO register-controlled.

Now that we convert the PDM input from the microphone to PCM, we need to modify the RX (receiving) fifo of the microphone to accept 32-bit inputs instead of 1-bit inputs, since PCM is 32-bits whilst PDM is 1-bit (in the case of the current design). At this stage we won't modify the TX (transmitting) fifo side.

![](/images/audio_direct_new.jpg)

Here's the new `audio_direct_v1_1` hierarchy we want to end up with. Here, we replace the old vhdl AXI4 peripheral file (XX_S_AXI_inst) with a newer Verilog version. Here are the files you need to import to replace the old files:

- [`audio_direct_v1_1.v`](/hw_files/audio_direct_v1_1.v)
- [`audio_direct_v1_1_S00_AXI.v`](/hw_files/audio_direct_v1_1_S00_AXI.v)
- [`pdm_rxtx.v`](/hw_files/pdm_rxtx.v)
- [`pdm_ser.v`](/hw_files/pdm_ser.v)

Some of them are verilog conterparts of the original vhdl files, while some are modified versions to support PCM data.
Compare the new hierarchy to the old hierarchy - do you notice any removed files? Think about which files you will need to modify, and which ones you won't need to.

Based on your experience so far in lab 1 and lab 2, you should be able to modify the old BaseOverlay `audio_direct` hierarchy into the new hierarchy which supports PCM, so here I will provide less instructions.

> As a hint, start from the design source files within the `audio_direct_v1_1` ip at the start of this section which you saw when you explored the BaseOverlay. The required files that you need to modify are provided in this repository under `hw_files`. Once you have finished, package the IP.

### Task 2D: Connecting up the modified modules

Now let's connect up the audio frontend we created in Task 2B and the modified `audio_direct` ip we developed in Task 2C.

Starting from the `lab2-skeleton`, we first add the two IPs built in Task 2C and 2D.

Firstly, make sure that this skeleton Vivado project can actually find the IPs you packaged. To do so, on the sidebar (Project Manager) click "Settings". Then in the pop-up, navigate to "IP > Repository". Add the path to where you saved your IP projects. If you saved all your Vivado projects under the same directory (e.g. `vivado_ws`), that makes it easier - just add the uppermost directory as one of the paths, and Vivado will auto-detect all the IPs within the directory.

![](/images/add_ip_path.jpg)

Next, you should be able to add the IPs to the block design. Connect up the IPs like this:

![](/images/design.jpg)

After completion of the design, we generate bitstream. Obtain the required `tcl`, `hwh` and `bit` files - repeating the steps you previously did in lab 1.

> Note: You can run "validate design" to do a simple check of your block design before running bitstream generation. Reference: <https://docs.amd.com/r/en-US/ug995-vivado-ip-subsystems-tutorial/Step-8-Validating-the-Design>

### Task 2E: Modifying the drivers

Next, we modify the Python drivers, as the drivers should now expect PCM data instead of PDM data. The theory is quite similar to the array merging drivers in Lab 1.

> Please first read the `driver_instructions.md` in the `pcm_driver` folder.

Before you follow the instructions and copy the new `audio.py`, let's understand what is happening in all of the files. As mentioned in the driver instructions files, a test/debug C++ driver was created for PCM. This did not exist in the original PYNQ codebase. The following link takes you to the original PYNQ C++ driver:

<https://github.com/Xilinx/PYNQ/blob/master/pynq/lib/_pynq/_audio/audio_direct.cpp>

Let's take a look at how the test/debug C++ driver works. Firstly, the register offsets relative to the base address of the AXI4 peripheral is defined as constants, as well as the transmit and receive FIFO flags. Secondly, we define two inline functions `Read32` and `Write32`, which allows us to read and write to these registers to control the AXI4 peripheral. Thirdly, we have the driver functions such as `record`, which controls the AXI4 peripheral to record and save the receiving FIFO data into our statically-allocated buffer.

The C++ drivers which you interact with in the PYNQ codebase (under `pynq/lib/_pynq/_audio`) does basically the same thing, except rather than creating a static buffer in C++, it relies on a buffer created in the `audio.py` Python driver.

Now let's take a look at the `new_audio.py`. For an easier diff, the functions are marked either `not changed` or `changed`, in comparison to PYNQ's original Python driver. As you should know from the `merge array` example in Lab 1, the Makefile first compiles the C++ drivers into a `libaudio.so` shared library file, which is then loaded by Python using the CFFI (C Foreign Function Interface). Main changes were made to the `record` and `save` functions, where the expected buffer data sampling rate and audio saving file type has been changed.

> Fun fact: I had some troubles debugging the specific sampling rate number to be used in the Python `record` function. Read `sample-rate.txt` for a fuller explanation.

> To make it clear, do not use the C++ or Makefile in the `pcm_driver` folder - read the instructions in the markdown file and only use the contents from the `new_audio.py`.

### Task 2F: Interacting with the drivers in Jupyter Notebook

After following the driver instructions, now let's interact with them in Jupyter Notebook.

Upload the `lab2-hw.ipynb` notebook from `jupyter_notebook/lab2` to your PYNQ board, similar to how you did it in lab 1 tasks. Running all the cells should record and save a file named "rec1.wav". Download that file to your local device, and try playing it with your OS's default audio player. Check that you can hear the full recorded audio.

> If you're not hearing anything, then try using an ILA to debug your hardware design: <https://www.youtube.com/watch?v=5-CR5MRGPJE>

## 2.4 Conclusion

Congratulations for completing Lab 2. You've now gained hands-on experience with both software and hardware audio processing on the PYNQ-Z1 board.

This foundation in audio processing and hardware-software co-design will be essential for the upcoming sections where you'll integrate speech recognition capabilities using the Whisper API. You now have a complete audio pipeline that can capture microphone input, convert it to standard PCM format in hardware, and save it as WAV files ready for further processing.
