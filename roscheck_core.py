from dataclasses import dataclass, asdict
import math

VERSION='0.2.2'
KH_PRESETS_M_PER_ATM={
'Manuscript calibration (21% O2 = 200 uM)':0.0009523809523809524,
'Pure water at 37 C (1.26e-3 M/atm)':1.26e-3,
'Physiological aqueous medium (1.06e-3 M/atm)':1.06e-3,
}
@dataclass(frozen=True)
class SeahorseData:
    condition_ocr: float
    maximal_ocr: float
    non_mito_ocr: float
@dataclass(frozen=True)
class RosResult:
    mode:str; oxygen_percent_atm:float; dissolved_o2_uM:float; f_mito:float; species:str; target_or_input_uM:float; f_leak:float; superoxide_upper_uM:float; peroxide_upper_uM:float; category:str; headline:str; explanation:str; assumptions:tuple
    def to_dict(self):
        d=asdict(self); d['assumptions']=list(self.assumptions); return d

def dissolved_o2_uM(o2_percent_atm,kh_m_per_atm,total_pressure_atm=1.0):
    if not 0<=o2_percent_atm<=100: raise ValueError('O2 percentage must be between 0 and 100% atm.')
    return kh_m_per_atm*(o2_percent_atm/100)*total_pressure_atm*1e6

def f_mito_from_seahorse(d):
    den=d.maximal_ocr-d.non_mito_ocr; num=d.condition_ocr-d.non_mito_ocr
    if den<=0: raise ValueError('Maximal OCR must exceed non-mitochondrial OCR.')
    if num<0: raise ValueError('Condition OCR cannot be below non-mitochondrial OCR.')
    v=num/den
    if v>1.25: raise ValueError('Calculated f_mito exceeds 1.25; check OCR values and FCCP optimisation.')
    return v

def classify(f):
    # User-defined visual/interpretive bands for ROS_Check v0.2.2:
    # <=4% green; >4-30% yellow; >30-100% orange; >100% red/impossible.
    if f>1:
        return 'Impossible','Physically impossible electron-leak requirement','Required f_leak exceeds 100% of available mitochondrial electron flow.'
    if f<=.04:
        return 'Feasible','Within the selected feasible range','Required f_leak is <=4% of mitochondrial electron flow. This is quantitatively feasible under the selected ROS_Check criterion, but feasibility does not establish the mechanism.'
    if f<=.30:
        return 'Biological warning / check your system','Elevated electron-leak requirement','Required f_leak is >4% and <=30% of mitochondrial electron flow. Check the biological system and obtain direct, system-specific evidence for electron diversion of this magnitude.'
    return 'Biological warning / check your system','Very high electron-leak requirement','Required f_leak is >30% but <=100% of mitochondrial electron flow. This is not mathematically impossible, but it is an extreme requirement that demands strong direct evidence.'
def calculate_maximum(o2_percent_atm,f_mito,f_leak,kh,total_pressure_atm=1.0):
    o2=dissolved_o2_uM(o2_percent_atm,kh,total_pressure_atm); so=o2*f_mito*f_leak; hp=so/2; cat,head,exp=classify(f_leak)
    return RosResult('Maximum oxidant level for entered f_leak',o2_percent_atm,o2,f_mito,'O2 radical anion and H2O2',f_leak*100,f_leak,so,hp,cat,head,exp,('Deliberately permissive pre-clearance upper bounds, not steady-state intracellular concentrations.','All entered f_leak is assumed to form O2 radical anion.','Two O2 radical anions yield one H2O2 by dismutation.','Scavenging, compartmentation, diffusion and enzymatic clearance are not subtracted.'))

def calculate_required_leak(o2_percent_atm,f_mito,target_uM,target_species,kh,total_pressure_atm=1.0):
    o2=dissolved_o2_uM(o2_percent_atm,kh,total_pressure_atm); avail=o2*f_mito
    f=(2*target_uM/avail if target_species=='H2O2' else target_uM/avail) if avail>0 else math.inf
    so=avail*f if math.isfinite(f) else math.inf; hp=so/2 if math.isfinite(so) else math.inf; cat,head,exp=classify(f)
    return RosResult('Required f_leak for target oxidant level',o2_percent_atm,o2,f_mito,target_species,target_uM,f,so,hp,cat,head,exp,('Target is treated as a pre-clearance production ceiling, not a measured steady-state concentration.','For H2O2, two O2 radical anions are required per H2O2.','Scavenging and clearance would increase the production burden.','Plausible f_leak does not establish identity, localisation or causality.'))
