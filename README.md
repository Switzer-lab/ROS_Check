# ROS_Check v0.2.2

Desktop Python/Tkinter edition.

Result interpretation/color bands:
- Green: f_leak <= 4% (feasible)
- Yellow: 4% < f_leak <= 30% (biological warning/check your system)
- Orange: 30% < f_leak <= 100% (very high; check your system)
- Red: f_leak > 100% (physically impossible)

Outputs remain deliberately permissive pre-clearance ceilings, not steady-state intracellular concentrations.
