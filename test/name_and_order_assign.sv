module TOP(CLK, RST, IN, IN2, reg1, OUT);
  input CLK, RST, IN, IN2;
  reg reg1,reg2,reg3;
  output reg1,OUT;
  wire in1;
  logic OUT,OUTOUT;
  logic IN,IN2;

  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg1 <= 1'b0;
    end else begin
      reg1 <= IN;
    end
  end

  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg2 <= 1'b0;
    end else begin
      reg2 <= func1(reg1);
    end
  end

  SUB sub(.CLK(CLK),.RST(RST),.IN(in1),.OUT1(OUTOUT));
  SUB2 sub2(CLK,RST, in1,
  	OUT);

endmodule

module SUB(CLK,RST,IN, OUT1);
  input CLK, RST, IN;
  output OUT1;
  reg reg1;
  logic IN;

endmodule

module SUB2(CLK,RST,IN, OUT2);
  input CLK, RST, IN;
  output OUT2;
  reg reg1;
  logic IN;

endmodule

