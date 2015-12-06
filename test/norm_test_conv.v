module TOP(CLK, RST, WRITE, READ, ADDR, WRITE_DATA, READ_DATA);
  input CLK,RST,WRITE,READ;
  input [2:0] ADDR;
  input [1:0] WRITE_DATA;
  output [1:0] READ_DATA;
  reg [4:3] reg0;
  wire wire1;
reg [ 1:0] [22:0] l1 [2:0];
reg [ 1:0] [22:0] l2 [2:0];
  integer num;
localparam PINK = 'd 0 ;localparam GREEN = 'd 1 ;localparam YELLOW = 'd 5 ;localparam BLUE = 'd 6 ;

  always @(posedge CLK) begin
    if(RST) begin
      reg0[4:3] <= 0;
    end else if(WRITE) begin
      case(ADDR)
        0:reg0[4:3] <= WRITE_DATA[1:0];
      endcase
    end
  end


  assign wire1 = 1'b1;
  

endmodule


module #(2,2) SUB2(input CLK,input RST,input IN, output OUT);
endmodule
