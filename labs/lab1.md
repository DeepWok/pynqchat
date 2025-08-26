# Lab 1: Introduction to PYNQ and Vivado

## 1.1 Environment setup

### Toolchain versions

To get started with the labs, we will first setup the required toolchain - this might be a bit troublesome, so please take advantage of the debugging notes `debug.md`.

In this lab, we will use the PYNQ-Z1 board, with PYNQ image v3.1, and Vivado version 2024.2.

> Tested Vivado versions:
> - 2020.2

If you encounter any issues, please first refer to the debugging notes `debug.md`, before approaching the TAs or the module leader.

Operating system requirements: Windows 10 or 11, Linux (Ubuntu)

- This lab was created, tested and verified on a Windows 10 laptop running the above versions of the toolchains.
- If you are using a MacOS device, options include:
  - Virtual machine (VM)
  - Using lab computers

### Step 1: Install Vivado

Go to the following [page](https://www.xilinx.com/support/download.html) to download Vivado.  For limited storage issues, refer to [debug.md](../debug.md/#limited-storage-space).

### Step 2: Flashing the PYNQ image

Download the [Pynq SD Card Image](https://www.pynq.io/boards.html) onto the Pynq SD Card. You can use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to write the image.

### Step 3: Setting up the board

Once you have flashed the PYNQ image onto your SD card, insert it into the PYNQ-Z1 board and connect the power supply. The board should be powered by either a micro-USB cable or a 5V power supply. Remember to switch the pin on the board to either use the USB or power supply.

![Power options on PYNQ Z1 board](../images/power_options_on_pynq_z1.jpg)

Let us now look into how the board works. The most important component is the Zynq-7000 System-On-Chip (SoC), which contains the Processing System (PS) made up of an ARM-Cortex A9 core, as well as the Programmable Logic (PL) which can be configured with custom hardware designs that we will soon create in Vivado. The block diagram for the Zynq-7000 SoC is shown below:

![Zynq-7000 SoC Block Diagram](../images/Zynq-7000SBlockDiagram.jpg)
(Source: https://www.mouser.co.uk/new/xilinx/xilinx-zynq-7000-socs/)

On top of this, the PYNQ framework provides a full Ubuntu-based Linux distribution on the SD card, with Linux drivers for the interfaces between the PS and PL, wrapped in Python libraries which makes the design easier. The following excerpt from Xilinx's introduction to PYNQ gives an excellent visual representation of the overall systems you will be working with:

| ![PYNQ Workshop Slide 9](../images/pynq-workshop-slide-9.png)  |
| ------------------------------------------------------------ |
| ![PYNQ Workshop Slide 10](../images/pynq-workshop-slide-10.png) |
| ![PYNQ Workshop Slide 12](../images/pynq-workshop-slide-12.png) |
(Source: https://github.com/Xilinx/PYNQ_Workshop/blob/master/01_PYNQ_Workshop_introduction.pdf)

### Step 4: Connecting to Jupyter Notebook

By default, PYNQ uses a web interface to interact with the FPGA board. We will now connect to the board's Jupyter Notebook server via Ethernet. Connect the Ethernet cable to the board and your computer. If your computer does not have an Ethernet port, you can use an Ethernet adapter.

> Note: if you connect Ethernet directly to your computer, PYNQ will not have access to the internet unless you bridge your computers internet connection. This means you will not be able to update system packages.

#### Assigning a Static IP:

PYNQ by default uses a static IP address of `192.168.2.99`. You should configure your laptop to also have an IP address **on the same subnet as the PYNQ-Z1 board** (i.e. `192.168.2.x`) to be able to access the Jupyter Notebook server.

__Windows__
Open up the `Network and Sharing Center`, and click on the `Ethernet connection`. Click on `Properties`, and then double-click on `Internet Protocol Version 4 (TCP/IPv4)`. Assign the following IP address: `192.168.2.x` where x is any number between 0 and 255, other than 99.

__Linux__
See the PYNQ documentation: https://pynq.readthedocs.io/en/latest/appendix/assign_a_static_ip.html#assign-a-static-ip-address

#### Open Notebook in browser

Now, open up your web browser and type in the following address: `192.168.2.99:9090`, which is PYNQ's default IP address. The default password is `xilinx`

> Is your PYNQ board refusing to connect? Refer to the troubleshooting section in [debug.md](../debug.md/#refusing-to-connect). Troubleshooting might require the use of a SSH/Serial terminal.

### Getting a terminal (optional)

You may have encountered terminals in various forms before in your work or previous modules. They can be very useful for controlling devices that are remote, low-powered, and/or have little I/O hardware of their own.

The section on getting a terminal in [debug.md](../debug.md/#getting-a-terminal) explains how to get a terminal, either via SSH or a Serial console.

Note that this is not strictly necessary, as you should be able to use the Juputer Notebook interface to directly interact with your PYNQ board. However, having a terminal is useful for troubleshooting in cases where your board refuses to establish a connection.

## 1.2 FIR filter

Now we are ready to get started. Open up Vivado and create a new project.

> Credits to [this tutorial](https://www.fpgadeveloper.com/2018/03/how-to-accelerate-a-python-function-with-pynq.html/) by Jeff Johnson for this section. If you get lost in this section, feel free to refer to his YouTube tutorial.

### Creating a new project

1. Open up Vivado and create a new project.
2. Press Next after reading the wizard.
3. Enter a suitable name and location for the project. Ensure check subdirectory is enabled so that your project files are contained in a parent folder.
4. Press Next.
5. Select RTL Project, for now: "do not specify the sources".
6. Press Next.
7. Select the PYNQ-Z1 board (you may need to install board files in Vivado, see below.) Double click on the part number to select it and move onto the summary.
8. Press Finish.

![Vivado Start Page](/images/starting_page.png)


![Vivado New Project Page](/images/new_project_page.png)


![Vivado Part Select Page](/images/part_select.png)

![Vivado New Project Wizard Summary](/images/new_project_summary.png)

> Board part troubleshooting: If you are unable to find the PYNQ-Z1 board, refer to the troubleshooting section in [debug.md](../debug.md/#board-parts-not-found). Note that instead of clicking on `Boards`, you may also directly select from `Parts` the board part part (xc7z020-1clg400c).

### Creating the block design

1. On the column on the left hand side, click `Create Block Design`. You can leave the block design name as `design_1` for now.

![Create Block Design](/images/create_block_design.png)

2. Add the Zynq7 processing system - this contains the interfaces to the dual ARM cores on the FPGA. Inside the Zynq7 PS IP settings, there is a part which notes how many HP slave ports are needed (only one needed in this case, HP0).

![Add Zynq Processing System IP](/images/add_ip.png)

//! Picture for adding ZYNQ7 Processing System (HP slave port)

3. Add the `Direct Memory Access` (DMA) block. <TODO: add explanation>

![Add AXI Direct Memory Access (DMA)](/images/dma.png)

3.1 Double click on the `AXI DMA` block to customise it.
3.2 Disable `Enable Scatter Gather Engine`,
3.3 Maximise the size of the `Width of Buffer Length Register` to 26 bits.
3.4 Press ok to exit the wizard.

4. Add the FIR filter: Vivado provides a wizard called the `FIR Compiler` which helps you to design your own filter. See <TODO: for more details>

![Add FIR Compiler Block](/images/fir_compiler.png)

4.1. Create the FIR filter by specifying the coefficients. Double click on the FIR Compiler block to customise the IP, and paste in the following coefficients:
```
-255, -260, -312, -288, -144, 153, 616, 1233, 1963, 2739, 3474, 4081, 4481, 4620, 4481, 4081, 3474, 2739, 1963, 1233, 616, 153, -144, -288, -312, -260, -255
```

4.2 Next, on the `Channel Specification` tab: change the `Input Sampling Frequency` and the `Clock Frequency` to 100MHz. Thus each clock tick on the FPGA will feed one input to the FIR filter.

4.3 On the Implementation tab: we should change the `Input Data Width` to 32 bits. We also want the output to have 32 bits, so select the `Output Rounding Mode` to `Non Symmetric Rounding Up` and then change the `Output Width` to 32 bits.

4.4 In the `Interface` tab, we specify how this block should communicate on the AXI bus, in this case, we should enable `Output TREADY` and `TLAST` via `Packet Framing`. It is slightly out of scope to read into the AXI Stream protocol, but if you are interested, you may want to read up on it.

4.5 Press OK to end the customise IP wizard.

5. Connect the DMA to the FIR Compiler block:

5.1 We connect the `M_AXIS_DATA` from the output of the FIR compiler to the `S_AXIS_S2MM` (Slave AXI interface for Stream-to-Memory-Mapped transfers) input port of the AXI DMA Block.

5.2 Then, we connect the `M_AXI_S2MM` (Master AXI interface for Stream-to-Memory-Mapped transfers) ouput port of the DMA to the `S_AXIS_DATA` input port of the FIR Compiler. This allows us to feed a memory-mapped data format used by the DMA into the streaming input of signal data that the FIR compiler expects.

5.3: Your block diagram should look like this:
![DMA to FIR Compiler Connections](/images/dma_to_fir_connection.png)

6. Now, we connect this up to the ZYNQ Processing System, so that the DMA can access the DDR Memory that is present in the PS.

6.1 Double click the ZYNQ7 Processing System to edit it, and double click on the `High Performance AXI Slave Ports` to edit them.
6.2 Enable one port, for example the `HP0` port.
6.3 Then save and exit the customization.

![Zynq Block Design](/images/zynq-block-design.png)

7. Run Block Automation <TODO: What does this do?>

![Block Automation](/images/block_automation.png)

8. Run Connection Automation, Vivado intelligently maps input ports and output ports together. Select all the ports in the tree view.

![Connection Automation](/images/connection_automation.png)

9. Rename the `FIR Compiler` block to `fir`, and the `AXI DMA` block to `fir_dma`. This will make it cleaner to access in the Jupyter Notebook when we are utilising these accelerators.
You should have a design that looks something like this:

![Final Block Design](/images/final_block_design.png)

### Exporting the hardware


### Loading the overlay on Jupyter Notebook

## 1.3 Simple register control (merge array)

Here we attempt a simple array merging procedure

Don't worry, the drivers have already been prewritten for you under the `drivers` folder. But before we make a simple copy and paste change, we should look at what is being done under the hood which allows you to simply make this change.

