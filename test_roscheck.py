import pytest
from roscheck_core import *
KH=KH_PRESETS_M_PER_ATM['Manuscript calibration (21% O2 = 200 uM)']
def test_o2(): assert dissolved_o2_uM(21,KH)==pytest.approx(200)
def test_seahorse(): assert f_mito_from_seahorse(SeahorseData(80,110,10))==pytest.approx(.7)
def test_green_4_percent(): assert classify(.04)[0]=='Feasible'
def test_yellow_above_4_to_30(): assert classify(.05)[0]=='Biological warning / check your system' and classify(.30)[1]=='Elevated electron-leak requirement'
def test_orange_above_30_to_100(): assert classify(.31)[1]=='Very high electron-leak requirement' and classify(1.0)[0]=='Biological warning / check your system'
def test_red_above_100(): assert classify(1.01)[0]=='Impossible'
