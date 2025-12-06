module mergeCore(
        input   clock,
        input   reset,
        input   start,
        input [31:0] fifoWrData,
        input   fifo1WrEn,
        input   fifo2WrEn,
        input   mergedFifoRdEn,
        output [31:0] mergedFifoRdData,
        output  reg done
    );


    wire fifo1Empty;
    wire fifo2Empty;
    reg [31:0] mergeFifoData;
    reg mergeFifoWrEn;
    reg fifo1RdEn;
    reg fifo2RdEn;
    reg [2:0] state;
    wire [31:0] fifo1Data;
    wire [31:0] fifo2Data;

    localparam  IDLE  = 'd0,
                COMPARE = 'd1,
                FLUSH_FIFO = 'd2,
                WRITE =  'd3,
                DONE = 'd4;

    always @(posedge clock) begin
        if(reset) begin
            state <= IDLE;
            fifo1RdEn <= 1'b0;
            fifo2RdEn <= 1'b0;
            mergeFifoWrEn <= 1'b0;
            done <= 1'b0;
        end
        else begin
            case(state)
                IDLE: begin
                    if(start) begin
                        state <= COMPARE;
                    end
                end
                COMPARE: begin
                    if(!fifo1Empty & !fifo2Empty) begin
                        if(fifo1Data < fifo2Data) begin
                            mergeFifoData <= fifo1Data;
                            mergeFifoWrEn <= 1'b1;
                            fifo1RdEn <= 1'b1;
                        end
                        else begin
                            mergeFifoData <= fifo2Data;
                            mergeFifoWrEn <= 1'b1;
                            fifo2RdEn <= 1'b1;
                        end
                        state <= WRITE;
                    end
                    else if(fifo1Empty & fifo2Empty) begin
                        state <= DONE;
                    end
                    else if(fifo1Empty) begin
                        state <= FLUSH_FIFO;
                        fifo2RdEn <= 1'b1;
                    end
                    else if(fifo2Empty) begin
                        state <= FLUSH_FIFO;
                        fifo1RdEn <= 1'b1;
                    end
                end
                FLUSH_FIFO: begin
                    if(fifo1Empty & fifo2Empty) begin
                        state <= DONE;
                        fifo1RdEn <= 1'b0;
                        fifo2RdEn <= 1'b0;
                        mergeFifoWrEn <= 1'b0;
                    end
                    else if(fifo1Empty) begin
                        fifo2RdEn <= 1'b1;
                        mergeFifoWrEn <= 1'b1;
                        mergeFifoData <= fifo2Data;
                    end
                    else if(fifo2Empty) begin
                        fifo1RdEn <= 1'b1;
                        mergeFifoWrEn <= 1'b1;
                        mergeFifoData <= fifo1Data;
                    end
                end
                WRITE: begin
                    fifo1RdEn <= 1'b0;
                    fifo2RdEn <= 1'b0;
                    mergeFifoWrEn <= 1'b0;
                    state <= COMPARE;
                end
                DONE: begin
                    done <= 1'b1;
                    if(!start) begin
                        done <= 1'b0;
                        state <= IDLE;
                    end
                end
                default:
                    state <= IDLE;
            endcase
        end
    end

    arrayFifo arrayFifo1 (
                  .clk(clock),      // input wire clk
                  .srst(reset),    // input wire srst
                  .din(fifoWrData),      // input wire [31 : 0] din
                  .wr_en(fifo1WrEn),  // input wire wr_en
                  .rd_en(fifo1RdEn),  // input wire rd_en
                  .dout(fifo1Data),    // output wire [31 : 0] dout
                  .full(),    // output wire full
                  .empty(fifo1Empty)  // output wire empty
              );

    arrayFifo arrayFifo2 (
                  .clk(clock),      // input wire clk
                  .srst(reset),    // input wire srst
                  .din(fifoWrData),      // input wire [31 : 0] din
                  .wr_en(fifo2WrEn),  // input wire wr_en
                  .rd_en(fifo2RdEn),  // input wire rd_en
                  .dout(fifo2Data),    // output wire [31 : 0] dout
                  .full(),    // output wire full
                  .empty(fifo2Empty)  // output wire empty
              );


    mergedFifo mergedFifo (
                   .clk(clock),      // input wire clk
                   .srst(reset),    // input wire srst
                   .din(mergeFifoData),      // input wire [31 : 0] din
                   .wr_en(mergeFifoWrEn),  // input wire wr_en
                   .rd_en(mergedFifoRdEn),  // input wire rd_en
                   .dout(mergedFifoRdData),    // output wire [31 : 0] dout
                   .full(),    // output wire full
                   .empty()  // output wire empty
               );

endmodule
