module TOP(CLK, RST, WRITE, READ, ADDR, WRITE_DATA, READ_DATA);
  input CLK,RST,WRITE,READ;
  input [2:0] ADDR;
  input [1:0] WRITE_DATA;
  output [1:0] READ_DATA;
  logic [4:3] reg0;
  logic wire1;
  logic [ 1:0][22:0] l1, l2[2:0];
  int num;
  enum logic [2:0] {PINK,GREEN,YELLOW=5,BLUE} color_e;


  always_ff @(posedge CLK) begin
    if(RST) begin
      reg0[4:3] <= 0;
    end else if(WRITE) begin
      case(ADDR)
        0:reg0[4:3] <= WRITE_DATA[1:0];
      endcase
    end
  end

  default disable iff(RST);

  assign wire1 = 1'b1;
  
  property ttttt;
  endproperty

endmodule


module SUB2(input CLK,input RST,input IN, output OUT);
endmodule
