set design BENCH
set topmodule TOPMODULE
set srcdir DESIGN_PATH/$design/
set workdir WORKDIR_HOLDER
set outputDir $workdir/output
file delete -force $outputDir
file mkdir $outputDir

read_xdc $srcdir/design.xdc
read_verilog $srcdir/$design.v

synth_design -top $topmodule -part xc7z020clg484-2
source $workdir/options.tcl

write_checkpoint -force $outputDir/post_route
report_timing_summary -file $outputDir/post_route_timing_summary.rpt
report_timing -sort_by group -max_paths 100 -path_type summary -file $outputDir/post_route_timing.rpt
report_clock_utilization -file $outputDir/clock_util.rpt
report_utilization -file $outputDir/post_route_util.rpt
report_power -file $outputDir/post_route_power.rpt
report_drc -file $outputDir/post_imp_drc.rpt
write_verilog -force $outputDir/cpu_impl_netlist.v
write_xdc -no_fixed_only -force $outputDir/cpu_impl.xdc