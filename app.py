import json, math, tkinter as tk
from tkinter import ttk, messagebox, filedialog
from roscheck_core import *
class App(tk.Tk):
 def __init__(self):
  super().__init__(); self.title('ROS_Check v0.2.2'); self.geometry('980x760'); self.minsize(900,680); self.result=None; self.build(); self.sync()
 def ent(self,p,r,t,v):
  a=ttk.Label(p,text=t); b=ttk.Entry(p,textvariable=v); a.grid(row=r,column=0,sticky='w',padx=4,pady=4); b.grid(row=r,column=1,sticky='ew',padx=4,pady=4); return [a,b]
 def state(self,ws,on):
  for w in ws:
   try:w.configure(state='normal' if on else 'disabled')
   except:pass
 def build(self):
  root=ttk.Frame(self,padding=12); root.pack(fill='both',expand=True)
  ttk.Label(root,text='ROS_Check v0.2.2',font=('Segoe UI',19,'bold')).pack(anchor='w'); ttk.Label(root,text='Quantitative chemical plausibility checks for mitochondrial O2 radical anion and H2O2 mechanisms').pack(anchor='w'); ttk.Label(root,text='Deliberately permissive pre-clearance upper bounds; not intracellular steady-state concentrations.',foreground='#8a4b00').pack(anchor='w',pady=(2,10))
  pan=ttk.Panedwindow(root,orient='horizontal'); pan.pack(fill='both',expand=True); L=ttk.Frame(pan,padding=8); R=ttk.Frame(pan,padding=8); pan.add(L,weight=1); pan.add(R,weight=1)
  o=ttk.LabelFrame(L,text='1. Oxygen availability',padding=10); o.pack(fill='x',pady=5); self.o2=tk.DoubleVar(value=5); self.kh=tk.StringVar(value=list(KH_PRESETS_M_PER_ATM)[0]); self.press=tk.DoubleVar(value=1); self.o2txt=tk.StringVar(); self.ent(o,0,'O2 (% atm)',self.o2); ttk.Label(o,text='Henry-law calibration').grid(row=1,column=0,sticky='w'); c=ttk.Combobox(o,textvariable=self.kh,values=list(KH_PRESETS_M_PER_ATM),state='readonly',width=43); c.grid(row=1,column=1,sticky='ew'); c.bind('<<ComboboxSelected>>',lambda e:self.oxygen()); self.ent(o,2,'Total pressure (atm)',self.press); ttk.Button(o,text='Update O2',command=self.oxygen).grid(row=3,column=0,sticky='w'); ttk.Label(o,textvariable=self.o2txt,font=('Segoe UI',10,'bold')).grid(row=3,column=1,sticky='w'); o.columnconfigure(1,weight=1)
  f=ttk.LabelFrame(L,text='2. Mitochondrial activity',padding=10); f.pack(fill='x',pady=5); self.fm=tk.StringVar(value='direct'); ttk.Radiobutton(f,text='Enter f_mito directly',variable=self.fm,value='direct',command=self.sync).grid(row=0,column=0,columnspan=2,sticky='w'); ttk.Radiobutton(f,text='Calculate f_mito from Seahorse/OCR',variable=self.fm,value='sea',command=self.sync).grid(row=1,column=0,columnspan=2,sticky='w'); self.fmito=tk.DoubleVar(value=.7); self.cond=tk.DoubleVar(value=80); self.maxo=tk.DoubleVar(value=110); self.non=tk.DoubleVar(value=10); self.direct=self.ent(f,2,'f_mito',self.fmito); self.sea=self.ent(f,3,'OCR under condition',self.cond)+self.ent(f,4,'FCCP maximal OCR',self.maxo)+self.ent(f,5,'Rot/antimycin-insensitive OCR',self.non); ttk.Label(f,text='Seahorse proton leak is not f_leak.',foreground='#555').grid(row=6,column=0,columnspan=2,sticky='w'); f.columnconfigure(1,weight=1)
  q=ttk.LabelFrame(L,text='3. Calculation',padding=10); q.pack(fill='x',pady=5); self.mode=tk.StringVar(value='required'); ttk.Radiobutton(q,text='Required f_leak for target oxidant level',variable=self.mode,value='required',command=self.sync).grid(row=0,column=0,columnspan=2,sticky='w'); ttk.Radiobutton(q,text='Maximum oxidant level for entered f_leak',variable=self.mode,value='maximum',command=self.sync).grid(row=1,column=0,columnspan=2,sticky='w'); self.spec=tk.StringVar(value='H2O2'); ttk.Label(q,text='Target oxidant').grid(row=2,column=0,sticky='w'); self.specbox=ttk.Combobox(q,textvariable=self.spec,values=['H2O2','O2 radical anion'],state='readonly'); self.specbox.grid(row=2,column=1,sticky='ew'); self.target=tk.DoubleVar(value=1); self.tw=self.ent(q,3,'Target level (uM)',self.target); self.leak=tk.DoubleVar(value=.5); self.lw=self.ent(q,4,'Entered f_leak (%)',self.leak); ttk.Button(q,text='Calculate',command=self.calc).grid(row=5,column=0,columnspan=2,sticky='ew',pady=(10,2)); q.columnconfigure(1,weight=1)
  x=ttk.LabelFrame(R,text='Result',padding=12); x.pack(fill='both',expand=True); self.status=tk.StringVar(value='Enter parameters and click Calculate.'); self.status_label=ttk.Label(x,textvariable=self.status,font=('Segoe UI',13,'bold'),wraplength=420); self.status_label.pack(anchor='w'); self.metrics=tk.StringVar(); ttk.Label(x,textvariable=self.metrics,font=('Consolas',11),justify='left').pack(anchor='w',pady=8); self.explain=tk.StringVar(); ttk.Label(x,textvariable=self.explain,wraplength=430,justify='left').pack(anchor='w'); ttk.Separator(x).pack(fill='x',pady=8); ttk.Label(x,text='Assumptions / limitations',font=('Segoe UI',10,'bold')).pack(anchor='w'); self.notes=tk.Text(x,height=11,wrap='word'); self.notes.pack(fill='both',expand=True); self.notes.configure(state='disabled'); b=ttk.Frame(x); b.pack(fill='x',pady=6); ttk.Button(b,text='Save JSON',command=self.save).pack(side='left'); ttk.Button(b,text='Copy summary',command=self.copy).pack(side='left',padx=6)
  ttk.Label(root,text='ROS_Check v0.2.2 | Research-use plausibility calculator',foreground='#666').pack(anchor='w')
 def oxygen(self):
  try:self.o2txt.set(f'Dissolved O2 = {dissolved_o2_uM(self.o2.get(),KH_PRESETS_M_PER_ATM[self.kh.get()],self.press.get()):.4g} uM')
  except Exception as e:self.o2txt.set(str(e))
 def sync(self):
  self.oxygen(); self.state(self.direct,self.fm.get()=='direct'); self.state(self.sea,self.fm.get()!='direct'); req=self.mode.get()=='required'; self.specbox.configure(state='readonly' if req else 'disabled'); self.state(self.tw,req); self.state(self.lw,not req)
 def getfm(self):
  return self.fmito.get() if self.fm.get()=='direct' else f_mito_from_seahorse(SeahorseData(self.cond.get(),self.maxo.get(),self.non.get()))

 def result_colour(self,r):
  pct=r.f_leak*100
  if pct>100: return '#b00020'      # red: impossible
  if pct>30: return '#e66a00'       # orange: very high
  if pct>4: return '#b38f00'        # yellow/gold: warning
  return '#14833b'                  # green: feasible
 def calc(self):
  try:
   kh=KH_PRESETS_M_PER_ATM[self.kh.get()]; fm=self.getfm(); r=calculate_required_leak(self.o2.get(),fm,self.target.get(),self.spec.get(),kh,self.press.get()) if self.mode.get()=='required' else calculate_maximum(self.o2.get(),fm,self.leak.get()/100,kh,self.press.get()); self.result=r; pre='FEASIBLE' if r.category=='Feasible' else ('IMPOSSIBLE' if r.category=='Impossible' else 'BIOLOGICAL WARNING / CHECK YOUR SYSTEM'); self.status.set(pre+': '+r.headline); self.status_label.configure(foreground=self.result_colour(r)); lk='infinite' if not math.isfinite(r.f_leak) else f'{100*r.f_leak:.4g}%'; self.metrics.set(f'Dissolved O2     {r.dissolved_o2_uM:.5g} uM\nf_mito           {r.f_mito:.5g}\nf_leak           {lk}\nO2 radical upper {r.superoxide_upper_uM:.5g} uM\nH2O2 upper       {r.peroxide_upper_uM:.5g} uM'); self.explain.set(r.explanation); self.notes.configure(state='normal'); self.notes.delete('1.0','end'); self.notes.insert('end','\n'.join('- '+z for z in r.assumptions)); self.notes.configure(state='disabled')
  except Exception as e:messagebox.showerror('ROS_Check',str(e))
 def save(self):
  if not self.result:return
  p=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('JSON','*.json')],initialfile='ROS_Check_result.json');
  if p:
   with open(p,'w',encoding='utf8') as h:json.dump(self.result.to_dict(),h,indent=2)
 def copy(self):
  if self.result:self.clipboard_clear(); self.clipboard_append(self.status.get()+'\n'+self.metrics.get()+'\n'+self.explain.get()); self.update()
if __name__=='__main__':App().mainloop()
