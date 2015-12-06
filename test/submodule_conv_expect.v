module TOP(CLK, RST, IN, IN2, reg1, OUT);
  input CLK, RST, IN, IN2;
  reg reg1,reg2,reg3;
  output reg1,OUT;
  wire in1;
  reg OUT;
wire IN;
wire IN2;

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

  SUB sub(CLK,RST,in1,OUT);
  SUB2 ccc(CLK,RST,in1);

  function func1;
    input bit1;
      if(bit1)
          func1 = !bit1;
      else
          func1 = bit1;
  endfunction

endmodule

module SUB(CLK,RST,IN, OUT);
  input CLK, RST, IN;
  output OUT;
  reg reg1;
  wire IN;
  wire OUT = reg1;

  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg1 <= 1'b0;
    end else begin
      reg1 <= 1'b1;
    end
  end

endmodule

module SUB2(input CLK,input RST,input IN, output OUT);
  reg reg1;
  wire IN;

  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg1 <= 1'b0;
    end else if(IN) begin
      reg1 <= 1'b0;
    end else begin
      reg1 <= 1'b1;
    end
  end

endmodule

