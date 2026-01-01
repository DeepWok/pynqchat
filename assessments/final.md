# Information Processing 

## Final Team Project

### Objective 

The overall goal is to develop an IoT system with multiple nodes that process data captured by an accelerometer and can interact with a cloud server in order for information to be exchanged. The aim is to bring together knowledge that you have acquired in the Autumn term and enhance your knowledge and practical skills through the development of such system. 

The nodes of the system consist of FPGA boards, where the server will be hosted on the cloud.  

The minimum functional requirements for your system are: 
- Local processing of data (on the FPGA SoC device).
- Establishing a cloud server to process events/information 
- Communicating information from the node to the server. 
- Communicating information from the server back to the nodes in way that the local processing can be impacted.  
- Use of at least two nodes and a demonstration of at least two nodes can both receive and transmit information
 
The project is open-ended, and it is your decision the detailed functionality of the system. A good approach is to start designing and developing a system for which it is easy to meet the above functional requirements, but also it has space for expansion. 

### Coursework deliverables 

Your coursework deliverables consist of the following: 

1. A report (pdf) that describes your system, consisting of at most 5 A4 pages. The report should cover: 
    - The purpose of your system. 
    - The overall architecture of your system. 
    - A description of the performance metrics of your system. Which metrics should be used? Why? 
    - At least one diagram of your system’s architecture. 
    - Design decisions taken when implementing the system, and an evaluation on these design choices.
    - The approach taken to test your system. 
    - At least one diagram or flow-chart describing your testing flow or approach. 
    - Resources utilised on the device, especially on the hardware resources.

2. Peer feedback: individual submission by each group member to provide peer feedback on your team members, submitted via Microsoft Forms. 
 
3. Your design (FPGA Hardware, only necessary), and software, in a Github Repository with clear instructions on how to run your code, the github link should be provided in the report. Do not submit code.
 
4. A short video (up to 10 min, through either a Youtube link for a link to download the video if making it publicly accessible is not preferred) where you can provide a description of your project and demonstrate what you have done.

### Assessment 

The coursework mark comes from the following components: 

* Functionality (30%) : does your system work? This is assessed purely based on whether the various parts of the system are functionally correct, and they meet the minimum functional requirements described above. 
* Testing (20%) : Is your testing complete? Have you considered testing all aspects of the system? 
* X-factor (20%) : This component aims to capture how challenging your system is and the optimisations that you have applied/considered. For example, when it comes to processing the data on the local node, this can be done with a direct implementation of an FIR filter using floats, a more optimised approach would be to consider performing the operations under a fixed-point representation, where an even more optimised approach would be to have a hardware component that performs the filtering. What are the trade-offs? 
* Documentation (20%) : Are the architectural and testing approached adequately described? Have the required components been covered? Does it provide useful information specific to your solution? Does it highlight any clever or important features/decisions? 
* Oral examination (10%) : An opportunity to demonstrate and explain your project.  
* Peer-feedback (+-10%) : allocated according to peer feedback within the group. This will affect the individual mark by up to 10% relative to the group mark. 

### Submission 

Submission will be through blackboard.  

It is up to you to choose/manage source code control through any tool or technology you want. You can get access to github pro through the github education programme, but you can use any other service your team prefers - if you want to work out of SharePoint, this is also fine.

Note that the Github repository should not contain any code for the labs, it should only contain the code for your team project, failure in doing so would result a reduction in marks.