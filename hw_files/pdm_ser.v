`timescale 1ns / 1ps

module pdm_ser #(
    parameter C_NR_OF_BITS = 32,
    parameter C_SYS_CLK_FREQ_MHZ = 100,
    parameter C_PDM_FREQ_MHZ = 3
)(
    input wire clk_i,
    input wire rst_i,
    input wire en_i,

    output reg done_o,
    input wire [C_NR_OF_BITS-1:0] data_i,

    // PWM
    output wire pwm_audio_o,
    output reg pwm_audio_t,
    input wire pwm_audio_i
);

// Signal Declarations
reg [6:0] cnt_clk;
reg clk_int, clk_intt;
wire pdm_clk_rising;
reg [C_NR_OF_BITS-1:0] pdm_s_tmp;
reg [4:0] cnt_bits;

// Module Implementation

// counter for the number of sampled bits
always @(posedge clk_i) begin
    if (rst_i) begin
        cnt_bits <= 0;
    end else if (pdm_clk_rising) begin
        if (cnt_bits == (C_NR_OF_BITS-1)) begin
            cnt_bits <= 0;
        end else begin
            cnt_bits <= cnt_bits + 1;
        end
    end
end

// done gen
always @(posedge clk_i) begin
    if (rst_i) begin
        done_o <= 1'b0;
    end else if (pdm_clk_rising) begin
        if (cnt_bits == (C_NR_OF_BITS-1)) begin
            done_o <= 1'b1;
        end
    end else begin
        done_o <= 1'b0;
    end
end

// Serializer
always @(posedge clk_i) begin
    if (rst_i) begin
        pdm_s_tmp <= 0;
    end else if (pdm_clk_rising) begin
        if (cnt_bits == (C_NR_OF_BITS-2)) begin // end of deserialization
            pdm_s_tmp <= data_i;
        end else begin
            pdm_s_tmp <= {pdm_s_tmp[C_NR_OF_BITS-2:0], 1'b0};
        end
    end
end

// output the serial pdm data
assign pwm_audio_o = 1'b0;
always @(*) begin
    if (en_i) begin
        pwm_audio_t = (pdm_s_tmp[C_NR_OF_BITS-1] == 1'b0) ? 1'b0 : 1'b1;
    end else begin
        pwm_audio_t = 1'b0;
    end
end

// slave clock generator
always @(posedge clk_i) begin
    if (rst_i) begin
        cnt_clk <= 0;
        clk_int <= 1'b0;
        clk_intt <= 1'b0;
    end else if (cnt_clk == ((C_SYS_CLK_FREQ_MHZ/(C_PDM_FREQ_MHZ*2))-1)) begin
        cnt_clk <= 0;
        clk_int <= ~clk_int;
        clk_intt <= clk_int;
    end else begin
        cnt_clk <= cnt_clk + 1;
        clk_intt <= clk_int;
    end
end

assign pdm_clk_rising = (clk_int == 1'b1 && clk_intt == 1'b0) ? 1'b1 : 1'b0;

endmodule
