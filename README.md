# systemverilog2verilog
Converting systemverilog code to verilog code.

Introduction
==============================
systemverilog2verilog is coverter of systemverilog to verilog.
This script is for adapting a tools which is not adapting a systemverilog.
Such as pyverilog, pyverilog_toolbox, pyeda, and etc.


Software Requirements
==============================
* Python (2.7)

Installation
==============================
git clone https://github.com/fukatani/systemverilog2verilog.git

Usage
==============================
python sv2v.py *systemverilog-file-name*

Features
==============================
logic: Convert to reg or wire.
bit: Convert to reg or wire.
byte: Convert to reg [7:0] or wire [7:0] .
enum: Expand to localparam.

e.g. 
```verilog
enum logic [2:0] {PINK,GREEN,YELLOW=5,BLUE} color_e;
```
->
```verilog
localparam PINK = 'd 0 ;localparam GREEN = 'd 1 ;localparam YELLOW = 'd 5 ;localparam BLUE = 'd 6 ;
```


(.*) port assign: Expand to assignment using port name.
clocking-endcloclking, property-endproperty, sequence-endsequence block: Delete all sentence.
default, assert: Delete line.
always_comb-> always @*
always_latch-> always @*
always_ff-> always
int-> integer
shortint-> reg signed [15:0]
longint-> reg signed [63:0]
'0-> 'd0
'1-> hffff
parameter logic-> parameter
localparam logic-> localparam
function logic-> function


Unimplemented:
interface (may be addressed in the future.)
struct (may be addressed in the future.)
union

License
==============================

Apache License 2.0
(http://www.apache.org/licenses/LICENSE-2.0)


Copyright
==============================

Copyright (C) 2015, Ryosuke Fukatani

