# Lab 1: Introduction to PYNQ and Vivado

## 1.1 Environment Setup

### Toolchain Versions

Before beginning the labs, you must first set up the required toolchain. This process may present some challenges, so please refer to the debugging notes in `debug.md` if you encounter any issues.

This lab uses the PYNQ-Z1 board and requires Windows or Linux for development. Please ensure you have **Vivado 2022.2** installed, as newer versions may have IP template changes that could affect the lab exercises.

> **Note:** This lab was originally developed on Windows 10 using PYNQ v2.7 and Xilinx Vivado 2020.2 (Kevin), and has been tested on Windows 11 using PYNQ v3.1 and Xilinx Vivado 2022.2 (Cheng).

**Important:** Vivado projects and TCL scripts are forward-compatible but not backward-compatible.

![versions](/images/lab1-pynq-versions.png)

> Source: <https://pynq.readthedocs.io/en/latest/pynq_sd_card.html>

If you encounter any issues, please first consult the debugging notes in `debug.md` before contacting the TAs or module leader.

**Operating System Requirements:** Windows 10/11 or Linux (Ubuntu)

- **MacOS users:** Please use one of the following options:
  - Virtual machine (VM)
  - Lab computers

### Step 1: Install Vivado

Download Vivado from the [Xilinx download page](https://www.xilinx.com/support/download.html). If you have limited storage space, refer to [debug.md](../debug.md/#limited-storage-space) for guidance.

### Step 2: Flash the PYNQ Image

Download the [PYNQ SD Card Image](https://www.pynq.io/boards.html) and write it to your SD card using [Raspberry Pi Imager](https://www.raspberrypi.com/software/) or a similar tool.

### Step 3: Set Up the Board

> 📝 **Watch the video:** [Setting up your PYNQ-Z1 board](https://www.youtube.com/watch?v=SuXkbcK3w9E) before proceeding.

After flashing the PYNQ image onto your SD card, insert it into the PYNQ-Z1 board and connect power. The board can be powered via either a micro-USB cable or a 5V power supply. Ensure the power jumper is set to the appropriate position (USB or external power).

![Power options on PYNQ Z1 board](../images/lab1-power-options-pynq-z1.jpg)

Let's examine how the board works. The central component is the Zynq-7000 System-on-Chip (SoC), which consists of:

- **Processing System (PS):** A dual-core ARM Cortex-A9 processor
- **Programmable Logic (PL):** FPGA fabric that can be configured with custom hardware designs

The block diagram for the Zynq-7000 SoC is shown below:

![Zynq-7000 SoC Block Diagram](../images/lab1-zynq-7000-block-diagram.jpg)

> Source: <https://www.mouser.co.uk/new/xilinx/xilinx-zynq-7000-socs/>

The PYNQ framework provides a complete Ubuntu-based Linux distribution on the SD card, including Linux drivers for the PS-PL interfaces wrapped in Python libraries for easier development. The following slides from Xilinx's PYNQ introduction provide an excellent visual representation of the system architecture:

| ![PYNQ Workshop Slide 9](../images/lab1-pynq-workshop-slide-9.png)  |
| ------------------------------------------------------------ |
| ![PYNQ Workshop Slide 10](../images/lab1-pynq-workshop-slide-10.png) |
| ![PYNQ Workshop Slide 12](../images/lab1-pynq-workshop-slide-12.png) |

> Source: <https://github.com/Xilinx/PYNQ_Workshop/blob/master/01_PYNQ_Workshop_introduction.pdf>

### Step 4: Connect to Jupyter Notebook

PYNQ uses a web-based Jupyter Notebook interface for interacting with the FPGA board. Connect an Ethernet cable between the board and your computer. If your computer lacks an Ethernet port, use an Ethernet adapter.

> **Note:** When connecting directly to your computer via Ethernet, PYNQ will not have internet access unless you bridge your computer's internet connection. Without internet access, you cannot update system packages.

#### Assign a Static IP Address

PYNQ uses the static IP address `192.168.2.99` by default. Configure your computer to use an IP address **on the same subnet** (i.e., `192.168.2.X`) to access the Jupyter Notebook server.

**Windows:**

1. Open `Network and Sharing Center`
2. Click on the `Ethernet connection`
3. Click `Properties`
4. Double-click `Internet Protocol Version 4 (TCP/IPv4)`
5. Assign a static IP address: `192.168.2.X` (where X is any number from 1-254, except 99)

**Linux:**
Refer to the PYNQ documentation: <https://pynq.readthedocs.io/en/latest/appendix/assign_a_static_ip.html#assign-a-static-ip-address>

#### Open Jupyter Notebook in Your Browser

Open your web browser and navigate to: `192.168.2.99:9090`. Enter the default password: `xilinx`

> **Connection Issues?** If your PYNQ board refuses to connect, refer to the troubleshooting section in [debug.md](../debug.md/#refusing-to-connect). You may need to use SSH or a serial terminal for debugging.

### Getting a Terminal (Optional)

Terminals are useful tools for controlling remote, low-powered devices with limited I/O hardware. While not strictly necessary (you can interact with PYNQ through the Jupyter Notebook interface), having terminal access is valuable for troubleshooting connection issues.

The [debug.md](../debug.md/#getting-a-terminal) guide explains how to access a terminal via SSH or serial console.

## 1.2 FIR Filter

You are now ready to create your first FPGA design. This section will guide you through implementing a Finite Impulse Response (FIR) filter.

> **Credits:** This section is based on [Jeff Johnson's tutorial](https://www.fpgadeveloper.com/2018/03/how-to-accelerate-a-python-function-with-pynq.html/). If you need additional guidance, refer to his YouTube tutorial. Thanks also to Sanjit Raman for providing screenshots. Note that some screenshots show Vivado 2024.2 on Ubuntu; your version may differ slightly, but the steps remain the same.

### Step 1: Create a New Project

1. Open Vivado and select **Create Project**
2. Click **Next** to proceed through the wizard
3. Enter a project name (e.g., `lab1`) and location. Ensure **Create project subdirectory** is checked
4. Click **Next**
5. Select **RTL Project** and choose **Do not specify sources at this time**
6. Click **Next**
7. Select the **PYNQ-Z1** board from the Boards tab. Double-click the part number to select it

    > 📝 **Can't find PYNQ-Z1?** Switch to the `Parts` tab and select `xc7z020clg400-1` directly.

8. Click **Finish**

![Vivado Start Page](/images/lab1-vivado-start-page.png)

![Vivado New Project Page](/images/lab1-vivado-new-project.png)

![Vivado Part Select Page](/images/lab1-vivado-part-select.png)

![Vivado New Project Wizard Summary](/images/lab1-vivado-project-summary.png)

> **Board Part Troubleshooting:** If you cannot find the PYNQ-Z1 board, refer to [debug.md](../debug.md/#board-parts-not-found). Alternatively, use the `Parts` tab to directly select the part number `xc7z020clg400-1`.

### Step 2: Create the Block Design

In the left sidebar under **IP INTEGRATOR**, click **Create Block Design**. You can use the default name `design_1`.

![Create Block Design](/images/lab1-create-block-design.png)
![Block Design](/images/lab1-block-design.png)

Add the **ZYNQ7 Processing System** IP to your block design. This component provides the interface to the dual ARM Cortex-A9 cores. Double-click the ZYNQ7 PS block to open its configuration. Note the section for HP (High Performance) slave ports—you'll need one port (HP0) for this design.

![Add Zynq Processing System IP](/images/lab1-add-zynq-ip.png)

Add the **AXI Direct Memory Access (DMA)** IP to your block design.

![Add AXI Direct Memory Access (DMA)](/images/lab1-add-dma-ip.png)

Double-click the `AXI DMA` block to configure it:

- **Disable** `Enable Scatter Gather Engine`
- Set `Width of Buffer Length Register` to **26 bits** (maximum)
- Click **OK** to save

Add the **FIR Compiler** IP to design your filter.

![Add FIR Compiler Block](/images/lab1-add-fir-compiler.png)

Double-click the FIR Compiler block to configure it. In the **Filter Options** tab, paste the following coefficients:

```
-255, -260, -312, -288, -144, 153, 616, 1233, 1963, 2739, 3474, 4081, 4481, 4620, 4481, 4081, 3474, 2739, 1963, 1233, 616, 153, -144, -288, -312, -260, -255
```

In the **Channel Specification** tab:

- Set `Input Sampling Frequency` to **100 MHz**
- Set `Clock Frequency` to **100 MHz**
- This ensures each clock cycle processes one filter input

In the **Implementation** tab:

- Set `Input Data Width` to **32 bits**
- Set `Output Rounding Mode` to **Non Symmetric Rounding Up**
- Set `Output Width` to **32 bits**

In the **Interface** tab:

- Enable **Output TREADY**
- Enable **TLAST** via `Packet Framing`
- (This configures the AXI Stream protocol communication)

Click **OK** to save the configuration.

Connect the IP blocks:

1. Connect `M_AXIS_DATA` (FIR Compiler output) → `S_AXIS_S2MM` (AXI DMA input)
   - This sends processed data from the filter to memory via DMA

2. Connect `M_AXIS_MM2S` (AXI DMA output) → `S_AXIS_DATA` (FIR Compiler input)
   - This feeds memory-mapped data from DMA into the filter's streaming interface

Your block diagram should look like this:
![DMA to FIR Compiler Connections](/images/lab1-dma-fir-connections.png)

Now, we connect this up to the ZYNQ Processing System, so that the DMA can access the DDR Memory that is present in the PS.

Double click the ZYNQ7 Processing System to edit it, and double click on the `High Performance AXI Slave Ports` to edit them. Enable one port, for example the `HP0` port. Then save and exit the customization.

![Zynq Block Design](/images/lab1-zynq-hp-ports.png)

Next, Run Block Automation.

![Block Automation](/images/lab1-block-automation.png)

Also, Run Connection Automation - Vivado intelligently maps input ports and output ports together. Select all the ports in the tree view.

![Connection Automation](/images/lab1-run-connection-automation-1.png)

Press F6 to validate your design. You will see incomplete address path warnings. Run Connection Automation again.

![Connection Automation](/images/lab1-connection-automation.png)

Rename the `FIR Compiler` block to `fir`, and the `AXI DMA` block to `fir_dma`. This will make it cleaner to access in the Jupyter Notebook when we are utilising these accelerators.

![Rename block](/images/lab1-rename-block.png)

You should have a design that looks something like this:

![Final Block Design](/images/lab1-final-block-design.png)

### Exporting the hardware

Now that the design is completed, click `F6` to validate your design. If validation is successful, double click on `design1.bd` under "Design Sources" in the "Sources" window. Then select "Create HDL wrapper". Once that is completed, Go to the sidebar on the left, and run "Generate Bitstream". This should automatically run Synthesis and Implementation.

![](/images/lab1-hdl-wrapper.jpg)

![](/images/lab1-export-hdl-wrapper.png)

> Synthesis translates your HDL code into a gate-level netlist of logical components (LUTs, flip-flops, DSPs, etc.) that can be implemented on the FPGA fabric. Implementation then places those components onto physical FPGA resources and routes the connections between them, while bitstream generation creates the binary configuration file that programs the FPGA.

Now to run your design on the PYNQ board, we need three files: a `tcl` file, a `hwh` files, and a `bit` file.

**Export the required files:**

1. **TCL file:** Go to **File → Export → Export Block Design**
2. **HWH file:** Navigate to `<project>/lab1.gen/sources_1/bd/design_1/hw_handoff/design_1.hwh`
3. **BIT file:** Navigate to `<project>/lab1.runs/impl_1/design_1_wrapper.bit` and rename it to `design_1.bit`

(Replace `<project>` with your actual project directory)

### Load the Overlay in Jupyter Notebook

1. Ensure your laptop is connected to the PYNQ board via Ethernet
2. Open a browser and navigate to `192.168.2.99:9090`
3. Enter the password: `xilinx`
4. Create a new folder (e.g., `InfoProc-lab1`)
5. Upload the three files (`.tcl`, `.hwh`, `.bit`) to this folder
6. Upload the provided Jupyter Notebook from `jupyter_notebook/lab1/fir.ipynb`

![jupyter](/images/lab1-jupyter-notebook.jpg)

7. Open the Jupyter Notebook and execute the cells
8. Follow the instructions and observe the performance difference between hardware and software implementations of the FIR filter

## 1.3 Simple Register Control (Merge Array)

This section demonstrates how Memory-Mapped I/O (MMIO) and register control work by implementing a hardware array merger that performs:

```
[1,3,5] + [2,4,6] => [1,2,3,4,5,6]
```

> **Reference:** For a similar design, watch [Make an RTL-based IP work with PYNQ - AXI Lite adder](https://youtu.be/RPTuhVeoGTI?si=gbzsbD1SdPM9QIfI)

### Step 1: Create the Block Design

#### 1.1 Create a New Project

Create a new Vivado project named `merge_array` following the same steps as Section 1.2.

#### 1.2 Create the Block Design

Create a block design and add the **ZYNQ7 Processing System**.

#### 1.3 Create the Merge Array IP

Select **Tools → Create and Package New IP** from the menu bar.

1. Choose **Create a new AXI4 peripheral**

![New AXI4 peripheral](/images/lab1-new-axi4-peripheral.jpg)

2. Name the peripheral `merge_array` with version `1.0`

![](/images/lab1-new-ip-package.jpg)

3. In the **Add Interfaces** page, set **Number of Registers** to **5**

![](/images/lab1-add-interfaces.jpg)

4. Select **Edit IP** and click **Finish**. Vivado will open a new project window for editing the IP.

![](/images/lab1-edit-ip.jpg)

#### 1.4 Modify the Merge Array IP

You will now customize the auto-generated AXI4-Lite interface template.

Open the **Sources** window and locate `merge_array_v1_0_S00_AXI.v`.

![](/images/lab1-edit-merge-ip.jpg)

**Add New Signal Declarations**

Locate the line `reg aw_en;` and add the following signals immediately after it:

```systemverilog
reg  aw_en;

// Add these new signals:
wire fsmStart;
wire sortDone;
reg fifo1_wr_en;
reg fifo2_wr_en;
wire [31:0] mergedFifoRdData;
```

**Add Control Signal Assignment**

Locate the line `assign S_AXI_RVALID = axi_rvalid;` and add the following immediately after:

```systemverilog
assign S_AXI_RVALID = axi_rvalid;

// Add this:
assign fsmStart = slv_reg0[0];
```

**Replace Register Write Logic**

Locate the large `always @(posedge S_AXI_ACLK)` block that handles register writes:

```systemverilog
always @( posedge S_AXI_ACLK )
begin
  if ( S_AXI_ARESETN == 1'b0 )
    begin
      slv_reg0 <= 0;
      slv_reg1 <= 0;
      slv_reg2 <= 0;
      slv_reg3 <= 0;
      slv_reg4 <= 0;
    end
  else begin
    if (slv_reg_wren)
      begin
        case ( axi_awaddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] )
          // ... all the case statements ...
        endcase
      end
  end
end
```

**Delete this entire block** and replace it with:

```systemverilog
// slv_reg0 handling
always @( posedge S_AXI_ACLK )
begin
  if ( S_AXI_ARESETN == 1'b0 )
    begin
      slv_reg0 <= 0;
    end
  else begin
    if (sortDone)
       slv_reg0 <= 0;
    if (slv_reg_wren && axi_awaddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] == 0)
       slv_reg0 <= S_AXI_WDATA;
  end
end

// slv_reg1 handling
always @( posedge S_AXI_ACLK )
begin
  if ( S_AXI_ARESETN == 1'b0 )
    begin
      slv_reg1 <= 0;
    end
  else begin
    if (sortDone)
       slv_reg1 <= 1;
    if (slv_reg_wren && axi_awaddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] == 1)
       slv_reg1 <= S_AXI_WDATA;
  end
end

// fifo1_wr_en handling (replaces slv_reg3)
always @( posedge S_AXI_ACLK )
begin
  if ( S_AXI_ARESETN == 1'b0 )
    begin
       fifo1_wr_en <= 0;
    end
  else begin
    if (sortDone)
       slv_reg0 <= 0;
    if (slv_reg_wren && axi_awaddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] == 3)
        fifo1_wr_en <= 1'b1;
    else
        fifo1_wr_en <= 1'b0;
  end
end

// fifo2_wr_en handling (replaces slv_reg4)
always @( posedge S_AXI_ACLK )
begin
  if ( S_AXI_ARESETN == 1'b0 )
    begin
       fifo2_wr_en <= 0;
    end
  else begin
    if (sortDone)
       slv_reg0 <= 0;
    if (slv_reg_wren && axi_awaddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] == 4)
        fifo2_wr_en <= 1'b1;
    else
        fifo2_wr_en <= 1'b0;
  end
end
```

**Update Register Read Logic**

Locate the `always @(*)` block for address decoding:

```systemverilog
always @(*)
begin
      // Address decoding for reading registers
      case ( axi_araddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] )
        3'h0   : reg_data_out <= slv_reg0;
        3'h1   : reg_data_out <= slv_reg1;
        3'h2   : reg_data_out <= slv_reg2;
        3'h3   : reg_data_out <= slv_reg3;
        3'h4   : reg_data_out <= slv_reg4;
        default : reg_data_out <= 0;
      endcase
end
```

**Replace with:**

```systemverilog
always @(*)
begin
      // Address decoding for reading registers
      case ( axi_araddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] )
        3'h0   : reg_data_out <= slv_reg0;
        3'h1   : reg_data_out <= slv_reg1;
        3'h2   : reg_data_out <= mergedFifoRdData;
        default : reg_data_out <= 0;
      endcase
end

assign mergedFifoRdEn = slv_reg_rden && (axi_araddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] == 2);
```

**Instantiate the Merge Core**

Find the "User logic" section near the end of the file. Replace:

```systemverilog
// Add user logic here

// User logic ends
```

**With:**

```systemverilog
// Add user logic here
mergeCore mc(
    .clock(S_AXI_ACLK),
    .reset(!S_AXI_ARESETN),
    .start(fsmStart),
    .fifoWrData(S_AXI_WDATA),
    .fifo1WrEn(fifo1_wr_en),
    .fifo2WrEn(fifo2_wr_en),
    .mergedFifoRdEn(mergedFifoRdEn),
    .mergedFifoRdData(mergedFifoRdData),
    .done(sortDone)
);

// User logic ends
```

#### Summary of Register Mapping

| Register Address | Modified Function |
|-----------------|--------------|
| 0x00 (slv_reg0) | Start bit + auto-clears when done |
| 0x04 (slv_reg1) | Status register (set to 1 when done) |
| 0x08 (slv_reg2) | **READ**: Merged FIFO output |
| 0x0C (slv_reg3) | **WRITE**: FIFO1 input (generates pulse) |
| 0x10 (slv_reg4) | **WRITE**: FIFO2 input (generates pulse) |

The transformation converts a passive register file into an active hardware controller with proper handshaking!

You have now transformed a standard AXI4 peripheral template into a custom hardware controller with proper register control and handshaking logic.

#### 1.5 Add the Merge Core Logic

The `mergeCore` module instantiated in the user logic section needs to be implemented.

1. In the **Sources** panel, click the **+** button
2. Select **Add or create design sources**
3. Click **Add Files** and navigate to [`hw_files/mergeCore.v`](../hw_files/mergeCore.v)
4. Click **OK** to add the file

![](/images/lab1-mergecore-ip.jpg)

You'll notice that `mergeCore.v` references FIFO modules that don't exist yet (indicated by red question marks).

![](/images/lab1-mergecore-hierarchy.jpg)

#### 1.6 Generate FIFO IPs

1. Click **IP Catalog** in the **Project Manager** section
2. Search for **FIFO Generator**
3. Double-click to open the configuration wizard

![](/images/lab1-fifo-generator.jpg)

**Configure the FIFOs:**

- Keep **Interface Type:** Native
- Keep **Clocking Mode:** Common Clock Block RAM
- Navigate to the **Native Ports** tab for the following changes:

![](/images/lab1-fifo-config.jpg)

![array-fifo](/images/lab1-array-fifo.png)

**Create two FIFO configurations:**

1. **arrayFifo** (for input arrays):
   - Component Name: `arrayFifo`
   - Write/Read Depth: **1024**
   - Data Width: **32 bits**

2. **mergedFifo** (for output):
   - Component Name: `mergedFifo`
   - Write/Read Depth: **2048**
   - Data Width: **32 bits**

> **Important:** The component names must exactly match the module instantiations in `mergeCore.v`.

After creating both FIFOs:

1. Navigate to **Package IP → Edit Packaged IP**
2. Review the **Identification** tab to note the IP version

![](/images/lab1-edit-pkg.png)

3. Select the **File Groups** tab. You should see 0 files included for the "Standard > Synthesis" file group.

![](/images/lab1-package-ip-file-groups.jpg)

Click on "**Merge changes from File Groups Wizard**". You should now see the hardware source files included.

![](/images/lab1-package-ip-file-groups-included.jpg)

If the above option does not show up, an alternate method is to add files manually. You can do so by right-clicking "**Synthesis**" file group, then selecting "**Add Files...**"

![](/images/lab1-package-ip-file-groups-manual.jpg)

4. Next, under **Review and Package**, click **Re-Package IP**

![](/images/lab1-package-ip.png)

5. Close the IP project and return to your main `merge_array` project

#### 1.7 Complete the Block Design

1. In the block diagram canvas, click the **+** button
2. Search for and add `merge_array_v1_0`

![](/images/lab1-add-merge-array-v1.0.png)

3. Run **Connection Automation** to connect the IP to the ZYNQ PS
4. Right-click `design_1` and select **Create HDL Wrapper**
5. Choose **Let Vivado manage wrapper and auto-update**

![](/images/lab1-create-hdl-wrapper.png)

#### 1.8 Generate Bitstream and Export Files

1. Click **Generate Bitstream** and wait for completion
2. Export the three required files:

   - **TCL:** **File → Export → Export Block Design**
   - **HWH:** `merge_array/merge_array.gen/sources_1/bd/design_1/hw_handoff/design_1.hwh`
   - **BIT:** `merge_array/merge_array.runs/impl_1/design_1_wrapper.bit` (rename to `design_1.bit`)

![](/images/lab1-export-block-design.jpg)

3. Upload all three files to a folder on your PYNQ Jupyter Notebook interface

### Step 2: Create the Drivers

With the hardware complete, you need software drivers to control it from Python.

Pre-written drivers are provided in the `drivers/merge_driver` folder. This section explains how they work and how to install them.

#### 2.1 Install Driver Files

Transfer the driver files to your PYNQ board using either SSH (PuTTY) or the Jupyter Notebook terminal.

![Placement of Merge Drivers in PYNQ](/images/lab1-merge-drivers-placement.jpg)

**File Structure:**

```
/home/xilinx/pynq/lib/
├── merge.py
└── _pynq/
    └── _merge/
        ├── merge_driver.cpp
        ├── merge_driver.h
        └── Makefile
```

**Build the Shared Library:**

1. Navigate to the driver directory:

   ```bash
   cd /home/xilinx/pynq/lib/_pynq/_merge
   ```

2. Compile the C++ code:

   ```bash
   make
   ```

3. Copy the compiled library:

   ```bash
   cp libmerge.so ../../
   ```

### Step 3: Understanding the Drivers

The driver creates a bridge between Python and your custom FPGA hardware, enabling register control and data transfer between the PS (ARM processor) and PL (FPGA fabric).

#### 3.1 C++ Driver Layer

**Header File (`merge_driver.h`):**
Defines memory-mapped register offsets for the merge IP core. These offsets are accessed as `BaseAddr + REGISTER_OFFSET`.

**Source File (`merge_driver.cpp`):**
Contains `merge_read()` and `merge_write()` functions that access hardware registers:

```c++
*(volatile uint32_t *)addr = data;
```

The `volatile` keyword ensures the compiler doesn't optimize away register accesses.

**The `merge()` Function:**

1. Writes each element of arrays `a` and `b` to `MERGE_1_REG` and `MERGE_2_REG`
2. Triggers the merge operation by writing `0x1` to `MERGE_CTRL_REG`
3. Polls `MERGE_STATUS_REG` until completion (reads 0)
4. Reads merged results from `MERGE_RESULT_REG` into `BufAddr`

The `extern "C"` linkage prevents C++ name mangling, enabling CFFI to call the function.

#### 3.2 Python Driver Layer

**How Python Controls C++ Functions:**

The Python driver uses **CFFI** (C Foreign Function Interface) to call compiled C++ code:

```python
self._libmerge = self._ffi.dlopen(os.path.join(LIB_SEARCH_PATH, "libmerge.so"))
```

CFFI handles type conversions automatically, providing a clean interface between Python and C/C++.

> **Why PYNQ?** Traditional FPGA development requires writing low-level C drivers. PYNQ simplifies this by providing pre-written drivers wrapped in Python, making FPGA development accessible to software engineers.

**Function Declarations:**

The `cdef()` calls declare C function signatures:

```python
self._ffi.cdef("void merge(unsigned int BaseAddr, ...);")
```

**MergeIP Class:**

Inherits from `DefaultIP`, integrating with PYNQ's overlay system:

```

- **`bindto`**: Specifies which Vivado IP block this driver controls (matches the VLNV identifier)
- **`self.mmio.array`**: Provides memory-mapped access to IP registers
- **`self.buffer`**: NumPy array for storing the merged output

**Data Flow: Python Arrays to C++ Pointers**

When you pass Python lists to the driver, they are converted to C++ pointers through CFFI. Here's the complete flow:

1. **Python Function Call:**
   ```python
   result = merge_ip.merge([1, 3, 5], [2, 4, 6])
   ```

2. **Convert to NumPy Arrays:**

   ```python
   a = numpy.array(a, dtype=numpy.uint32)  # [1, 3, 5]
   b = numpy.array(b, dtype=numpy.uint32)  # [2, 4, 6]
   ```

3. **Get Memory Addresses:**
   NumPy stores data in contiguous memory. The `ctypes.data` attribute returns the memory address:

   ```python
   a.ctypes.data  # Memory address as integer
   b.ctypes.data  # Memory address as integer
   ```

4. **Cast to C Pointers:**
   CFFI converts Python integers to C-style pointers:

   ```python
   a_ptr = self._ffi.cast("unsigned int *", a.ctypes.data)
   b_ptr = self._ffi.cast("unsigned int *", b.ctypes.data)
   ```

5. **Call C++ Function:**

   ```python
   self._libmerge.merge(
       self._base_addr,  # BaseAddr
       c_buf,            # BufAddr
       a_ptr,            # unsigned int *a
       a_size,           # a_size
       b_ptr,            # unsigned int *b
       b_size            # b_size
   )
   ```

**Zero-Copy Access:** C++ directly accesses the NumPy array memory—no data copying occurs. Both Python and C++ work with the same memory buffer, maximizing efficiency.

### Step 4: Run the Jupyter Notebook

1. Upload the provided Jupyter Notebook from `jupyter_notebook/lab1/Merge.ipynb` to your PYNQ board
2. Ensure the three hardware files (`.bit`, `.hwh`, `.tcl`) are in the same directory
3. Open the notebook and execute all cells
4. Verify that the merged array is correctly printed

The hardware accelerator should successfully merge the two input arrays, demonstrating the complete hardware-software integration using MMIO and custom IP cores.
