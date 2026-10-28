"""Editor visual didático para balanço térmico de ciclos a vapor.

Execute com Python 3: python balanco_termico.py
Usa somente a biblioteca padrão (Tkinter). Propriedades termodinâmicas são entradas.
"""
import csv
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from thermal_calculations import turbine_efficiency, pump_efficiency, preheater_effectiveness, heat_duty

BG = "#f2f5f9"
KINDS = {
    "Caldeira": ("#fff0ce", "P (bar)", "T (°C)", "h (kJ/kg)", "Vazão (kg/s)"),
    "Turbina": ("#e5efff", "P (bar)", "T (°C)", "h (kJ/kg)", "Vazão (kg/s)"),
    "Gerador": ("#e4f5f1", "Potência (MW)", "", "", ""),
    "Condensador": ("#e5f6fa", "P (bar)", "T (°C)", "h (kJ/kg)", "Vazão (kg/s)"),
    "Preaquecedor": ("#fff0ce", "P vapor (bar)", "T saída (°C)", "h saída (kJ/kg)", "Vazão (kg/s)"),
    "Desaerador": ("#eaf4ff", "P (bar)", "T saída (°C)", "h saída (kJ/kg)", "Vazão (kg/s)"),
    "Bomba": ("#e8f4f5", "P saída (bar)", "T saída (°C)", "h saída (kJ/kg)", "Vazão (kg/s)"),
    "Processo": ("#f1eaff", "P vapor (bar)", "T (°C)", "h (kJ/kg)", "Vazão (kg/s)"),
    "Misturador": ("#edf1f5", "P (bar)", "T (°C)", "h (kJ/kg)", "Vazão (kg/s)"),
}
DEFAULTS = {
    "Caldeira": [103, 543, 3481.3, 47.2], "Turbina": [15, 201, 2850, 47.2],
    "Gerador": [39.433, 0, 0, 0], "Condensador": [.1, 47.2, 2580, 39.6],
    "Preaquecedor": [15, 130, 550, 47.2], "Desaerador": [2.5, 127.4, 534, 47.2],
    "Bomba": [103, 130, 550, 47.2], "Processo": [15, 201, 2850, 7.6],
    "Misturador": [2.5, 100, 420, 47.2],
}

class ThermalEditor:
    def __init__(self, root):
        self.root = root; root.title("Balanço Térmico | Editor de Ciclo a Vapor"); root.geometry("1240x790"); root.minsize(900, 620); root.configure(bg=BG)
        self.nodes = {}; self.edges = []; self.streams = {}; self.next_id = 1; self.selected = None; self.selected_edge = None; self.drag = None; self.connect_from = None
        self._styles(); self._layout(); self._seed(); self.redraw()

    def _styles(self):
        s=ttk.Style(); s.theme_use("clam"); s.configure("TFrame",background=BG); s.configure("Card.TFrame",background="white"); s.configure("TLabel",background="white",foreground="#183047",font=("Segoe UI",10)); s.configure("Title.TLabel",font=("Segoe UI",16,"bold")); s.configure("TButton",padding=7); s.configure("Accent.TButton",background="#2468e8",foreground="white")

    def _layout(self):
        bar=ttk.Frame(self.root,padding=(16,12));bar.pack(fill="x");ttk.Label(bar,text="Balanço Térmico",style="Title.TLabel").pack(side="left");ttk.Label(bar,text="Editor visual de ciclo a vapor · protótipo de engenharia",foreground="#607389").pack(side="left",padx=16)
        actions=ttk.Frame(bar);actions.pack(side="right")
        for text,cmd in [("Conectar",self.start_connect),("Simular",self.simulate),("Excluir",self.delete_selected),("Salvar projeto",self.save_project),("Abrir projeto",self.open_project),("Exportar CSV",self.export_csv)]: ttk.Button(actions,text=text,command=cmd).pack(side="left",padx=3)
        body=ttk.Frame(self.root,padding=(12,0,12,12));body.pack(fill="both",expand=True)
        left=ttk.Frame(body,style="Card.TFrame",padding=12);left.pack(side="left",fill="y",padx=(0,10));ttk.Label(left,text="COMPONENTES",font=("Segoe UI",10,"bold")).pack(anchor="w",pady=(0,8))
        self.kind= tk.StringVar(value="Preaquecedor");ttk.Combobox(left,textvariable=self.kind,values=list(KINDS),state="readonly",width=19).pack(fill="x");ttk.Button(left,text="＋ Adicionar ao diagrama",command=self.add_component,style="Accent.TButton").pack(fill="x",pady=(6,12))
        ttk.Separator(left).pack(fill="x",pady=8);ttk.Label(left,text="PROPRIEDADES",font=("Segoe UI",10,"bold")).pack(anchor="w")
        self.prop_title=tk.StringVar(value="Selecione um componente");ttk.Label(left,textvariable=self.prop_title,font=("Segoe UI",11,"bold")).pack(anchor="w",pady=(8,4));self.prop_fields=[]
        self.prop_box=ttk.Frame(left,style="Card.TFrame");self.prop_box.pack(fill="x")
        ttk.Button(left,text="Aplicar valores",command=self.apply_properties).pack(fill="x",pady=8)
        ttk.Separator(left).pack(fill="x",pady=8);ttk.Label(left,text="INDICADORES",font=("Segoe UI",10,"bold")).pack(anchor="w")
        self.summary=tk.StringVar();ttk.Label(left,textvariable=self.summary,wraplength=210,justify="left").pack(anchor="w",pady=8)
        ttk.Label(left,text="Arraste blocos para mudar o layout. Selecione ‘Conectar’ e clique em dois blocos para criar/remover correntes. Clique numa corrente para editar os seus dados.",wraplength=210,foreground="#607389").pack(anchor="w",pady=8)
        area=ttk.Frame(body,style="Card.TFrame");area.pack(side="left",fill="both",expand=True)
        self.canvas=tk.Canvas(area,bg="#fbfdff",highlightthickness=0);self.canvas.pack(fill="both",expand=True);self.canvas.bind("<Button-1>",self.click);self.canvas.bind("<B1-Motion>",self.move);self.canvas.bind("<ButtonRelease-1>",self.release)
        self.status=tk.StringVar(value="Pronto · conecte os equipamentos seguindo o fluxo de massa.");ttk.Label(self.root,textvariable=self.status,anchor="w",padding=(15,6)).pack(fill="x")

    def _seed(self):
        data=[("Caldeira",100,160),("Turbina",370,160),("Gerador",650,160),("Preaquecedor",370,360),("Condensador",650,360),("Bomba",100,360)]
        for k,x,y in data:self._add(k,x,y)
        ids=list(self.nodes);self.edges=[(ids[0],ids[1]),(ids[1],ids[2]),(ids[1],ids[3]),(ids[1],ids[4]),(ids[4],ids[5]),(ids[5],ids[3]),(ids[3],ids[0])]
        for a,b in self.edges:self._init_stream(a,b)

    def _init_stream(self,a,b):
        src=self.nodes[a];v=src['v'];self.streams[f"{a}:{b}"]={"m":float(v[3]),"p":float(v[0]),"t":float(v[1]),"h":float(v[2])}

    def _add(self,k,x,y):
        i=self.next_id;self.next_id+=1;self.nodes[i]={"kind":k,"x":x,"y":y,"v":list(DEFAULTS[k]),"spec":{"eta":85.0,"h_is":None,"h_target":None}};return i
    def add_component(self):
        x=180+(len(self.nodes)%4)*55;y=120+(len(self.nodes)%4)*55;i=self._add(self.kind.get(),x,y);self.select(i);self.redraw()
    def redraw(self):
        c=self.canvas;c.delete("all")
        for a,b in self.edges:
            if a in self.nodes and b in self.nodes:
                n,m=self.nodes[a],self.nodes[b];c.create_line(n['x']+75,n['y']+31,m['x']+75,m['y']+31,fill="#778ba1",width=2,arrow="last",arrowshape=(9,11,4),tags=(f"edge{a}_{b}",))
        for i,n in self.nodes.items():
            color=KINDS[n['kind']][0];outline="#2468e8" if i==self.selected else "#bccada";x,y=n['x'],n['y']
            c.create_rectangle(x,y,x+150,y+62,fill=color,outline=outline,width=2,tags=(f"node{i}",));c.create_text(x+75,y+20,text=n['kind'],font=("Segoe UI",10,"bold"),fill="#183047",tags=(f"node{i}",));v=n['v'];detail=f"P {v[0]:g} bar  ·  m {v[3]:g} kg/s" if n['kind']!="Gerador" else f"{v[0]:g} MW";c.create_text(x+75,y+43,text=detail,font=("Segoe UI",8),fill="#50647a",tags=(f"node{i}",))
        self.update_summary()
    def click(self,e):
        item=self.canvas.find_withtag("current");tags=self.canvas.gettags(item[0]) if item else [];nid=next((int(t[4:]) for t in tags if t.startswith("node")),None);edge_tag=next((t for t in tags if t.startswith("edge")),None)
        if edge_tag and self.connect_from is None:
            a,b=map(int,edge_tag[4:].split("_"));self.selected_edge=(a,b);self.selected=None;self.show_stream(a,b);self.redraw();return
        if self.connect_from is not None:
            if self.connect_from == -1 and nid:
                self.connect_from=nid;self.status.set("Agora clique no componente de destino.");return
            if nid and nid!=self.connect_from:
                edge=(self.connect_from,nid)
                if edge in self.edges:self.edges.remove(edge);self.streams.pop(f"{edge[0]}:{edge[1]}",None)
                else:self.edges.append(edge);self._init_stream(*edge)
                self.status.set("Ligação atualizada.")
            self.connect_from=None;self.redraw();return
        self.select(nid);self.drag=(nid,e.x,e.y) if nid else None;self.redraw()
    def move(self,e):
        if self.drag and self.drag[0]:
            i,x,y=self.drag;n=self.nodes[i];n['x']=max(0,n['x']+e.x-x);n['y']=max(0,n['y']+e.y-y);self.drag=(i,e.x,e.y);self.redraw()
    def release(self,e):self.drag=None
    def select(self,i):
        self.selected=i;self.selected_edge=None
        for w in self.prop_box.winfo_children():w.destroy()
        self.prop_fields=[]
        if not i or i not in self.nodes:self.prop_title.set("Selecione um componente");return
        n=self.nodes[i];self.prop_title.set(f"{n['kind']} · #{i}");labels=KINDS[n['kind']][1:]
        for j,(label,val) in enumerate(zip(labels,n['v'])):
            if not label:continue
            row=ttk.Frame(self.prop_box,style="Card.TFrame");row.pack(fill="x",pady=3);ttk.Label(row,text=label).pack(anchor="w");var=tk.StringVar(value=str(val));ttk.Entry(row,textvariable=var,width=23).pack(fill="x");self.prop_fields.append((j,var))
        spec=n.setdefault('spec',{"eta":85.0,"h_is":None,"h_target":None})
        extras=[]
        if n['kind']=="Turbina":extras=[("eta","Eficiência isentrópica alvo (%)"),("h_is","Entalpia isentrópica de saída (kJ/kg)")]
        elif n['kind']=="Bomba":extras=[("eta","Eficiência isentrópica alvo (%)"),("h_is","Entalpia isentrópica de saída (kJ/kg)")]
        elif n['kind']=="Preaquecedor":extras=[("h_target","Entalpia-alvo da água (kJ/kg)")]
        for key,label in extras:
            row=ttk.Frame(self.prop_box,style="Card.TFrame");row.pack(fill="x",pady=3);ttk.Label(row,text=label).pack(anchor="w");var=tk.StringVar(value="" if spec.get(key) is None else str(spec[key]));ttk.Entry(row,textvariable=var,width=23).pack(fill="x");self.prop_fields.append((f"spec:{key}",var))
    def show_stream(self,a,b):
        for w in self.prop_box.winfo_children():w.destroy()
        self.prop_fields=[];self.prop_title.set(f"Corrente {a} → {b}")
        data=self.streams.setdefault(f"{a}:{b}",{"m":0,"p":0,"t":0,"h":0})
        for j,(key,label) in enumerate([("m","Vazão mássica (kg/s)"),("p","Pressão (bar)"),("t","Temperatura (°C)"),("h","Entalpia (kJ/kg)")]):
            row=ttk.Frame(self.prop_box,style="Card.TFrame");row.pack(fill="x",pady=3);ttk.Label(row,text=label).pack(anchor="w");var=tk.StringVar(value=str(data[key]));ttk.Entry(row,textvariable=var,width=23).pack(fill="x");self.prop_fields.append((key,var))
    def apply_properties(self):
        if self.selected_edge:
            a,b=self.selected_edge;data=self.streams[f"{a}:{b}"]
            try:
                for key,var in self.prop_fields:data[key]=float(var.get().replace(',','.'))
            except ValueError:messagebox.showerror("Valor inválido","Use valores numéricos para os campos.");return
            self.redraw();self.status.set("Dados da corrente atualizados.");return
        if self.selected not in self.nodes:return
        try:
            for j,var in self.prop_fields:
                value=var.get().replace(',','.').strip()
                if isinstance(j,str) and j.startswith("spec:"):
                    self.nodes[self.selected].setdefault('spec',{})[j.split(":",1)[1]]=None if not value else float(value)
                elif value:self.nodes[self.selected]['v'][j]=float(value)
        except ValueError:messagebox.showerror("Valor inválido","Use valores numéricos para os campos.");return
        self.redraw();self.status.set("Parâmetros aplicados.")
    def start_connect(self):self.status.set("Modo conexão: clique no primeiro e depois no segundo componente.");self.connect_from=-1
    def delete_selected(self):
        if self.selected in self.nodes:
            i=self.selected;del self.nodes[i];removed=[e for e in self.edges if i in e];self.edges=[e for e in self.edges if i not in e]
            for a,b in removed:self.streams.pop(f"{a}:{b}",None)
            self.selected=None;self.select(None);self.redraw()
        elif self.selected_edge:
            a,b=self.selected_edge;self.edges.remove((a,b));self.streams.pop(f"{a}:{b}",None);self.selected_edge=None;self.select(None);self.redraw()
    def update_summary(self):
        gen=sum(n['v'][0] for n in self.nodes.values() if n['kind']=="Gerador");flow=sum(n['v'][3] for n in self.nodes.values() if n['kind']=="Caldeira");q=sum(n['v'][3]*n['v'][2]/1000 for n in self.nodes.values() if n['kind']=="Processo");self.summary.set(f"Componentes: {len(self.nodes)}\nLigações: {len(self.edges)}\nPotência dos geradores: {gen:.2f} MW\nVazão informada em caldeiras: {flow:.2f} kg/s\nCalor estimado de processo: {q:.2f} MW")
    def simulate(self):
        """Resolve os balanços de cada equipamento a partir das correntes inseridas."""
        report=["RELATÓRIO DE SIMULAÇÃO · BALANÇO DE MASSA E ENERGIA", "", "Resíduos: Σ entrada − Σ saída. Potência térmica = m·h / 1000 (MW).", "Resultados dependem dos estados informados nas correntes.", ""]
        if not self.edges:messagebox.showwarning("Sem correntes","Conecte pelo menos duas unidades antes de simular.");return
        issues=[]
        for i,n in self.nodes.items():
            incoming=[self.streams.get(f"{a}:{b}",{}) for a,b in self.edges if b==i];outgoing=[self.streams.get(f"{a}:{b}",{}) for a,b in self.edges if a==i]
            if not incoming and not outgoing:continue
            mi=sum(s.get('m',0) for s in incoming);mo=sum(s.get('m',0) for s in outgoing);ei=sum(s.get('m',0)*s.get('h',0) for s in incoming)/1000;eo=sum(s.get('m',0)*s.get('h',0) for s in outgoing)/1000
            rm=mi-mo;re=ei-eo
            label=f"#{i} {n['kind']}";report.append(f"{label}: ṁ entrada {mi:.3f} | saída {mo:.3f} kg/s | resíduo {rm:+.3f} kg/s");report.append(f"    H entrada {ei:.3f} | saída {eo:.3f} MW | resíduo {re:+.3f} MW")
            try:
                spec=n.setdefault('spec',{"eta":85.0,"h_is":None,"h_target":None})
                if n['kind']=="Turbina" and incoming and outgoing and spec.get('h_is') is not None:
                    hin=sum(s['m']*s['h'] for s in incoming)/mi;hout=sum(s['m']*s['h'] for s in outgoing)/mo
                    report.append(f"    Eficiência isentrópica estimada: {turbine_efficiency(hin,hout,spec['h_is']):.2f}%")
                elif n['kind']=="Bomba" and incoming and outgoing and spec.get('h_is') is not None:
                    hin=sum(s['m']*s['h'] for s in incoming)/mi;hout=sum(s['m']*s['h'] for s in outgoing)/mo
                    report.append(f"    Eficiência isentrópica estimada: {pump_efficiency(hin,hout,spec['h_is']):.2f}%")
                elif n['kind']=="Preaquecedor" and incoming and outgoing and spec.get('h_target') is not None:
                    # A corrente de menor entalpia é tratada como água de alimentação.
                    sin=min(incoming,key=lambda s:s['h']);sout=min(outgoing,key=lambda s:s['h'])
                    report.append(f"    Efetividade térmica estimada: {preheater_effectiveness(sin['h'],sout['h'],spec['h_target']):.2f}%")
                elif n['kind'] in ("Turbina","Bomba","Preaquecedor"):
                    report.append("    Desempenho: preencha a entalpia isentrópica/alvo nas propriedades do equipamento.")
                if n['kind'] in ("Turbina","Bomba","Preaquecedor") and incoming and outgoing:
                    report.append(f"    Transferência/consumo calculado (resíduo H): {re:+.3f} MW")
            except (ValueError, ZeroDivisionError, KeyError) as ex:
                report.append(f"    Não foi possível calcular desempenho: {ex}")
            if abs(rm)>0.01:issues.append(f"{label}: balanço de massa não fecha ({rm:+.3f} kg/s)")
            if any(s.get('m',0)<0 or s.get('p',0)<=0 or s.get('h',0)<0 for s in incoming+outgoing):issues.append(f"{label}: corrente com valor inválido ou incompleto")
        report.extend(["", "DIAGNÓSTICOS"]);report.extend(["• "+x for x in issues] if issues else ["• Sem resíduos de massa acima da tolerância de 0,01 kg/s."])
        report.extend(["", "Nota: o resíduo de energia indica calor ou trabalho líquido requerido pelo equipamento; o protótipo ainda não possui solver IAPWS nem modelos de eficiência de máquina."])
        win=tk.Toplevel(self.root);win.title("Resultados da simulação");win.geometry("760x560");box=tk.Text(win,wrap="word",font=("Consolas",10),padx=14,pady=14);box.pack(fill="both",expand=True);box.insert("1.0","\n".join(report));box.configure(state="disabled")
        self.status.set(f"Simulação concluída · {len(issues)} alerta(s) de balanço/entrada.")
    def save_project(self):
        p=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("Projeto Balanço Térmico","*.json")])
        if p:
            with open(p,"w",encoding="utf-8") as f:json.dump({"nodes":self.nodes,"edges":self.edges,"streams":self.streams,"next_id":self.next_id},f,ensure_ascii=False,indent=2)
            self.status.set("Projeto salvo.")
    def open_project(self):
        p=filedialog.askopenfilename(filetypes=[("Projeto Balanço Térmico","*.json")])
        if p:
            try:
                with open(p,encoding="utf-8") as f:d=json.load(f)
                self.nodes={int(i):n for i,n in d['nodes'].items()};self.edges=[tuple(e) for e in d['edges']];self.streams=d.get('streams',{});self.next_id=d.get('next_id',max(self.nodes,default=0)+1)
                for a,b in self.edges:self._init_stream(a,b) if f"{a}:{b}" not in self.streams else None
                self.redraw();self.status.set("Projeto carregado.")
            except Exception as ex:messagebox.showerror("Falha ao abrir",str(ex))
    def export_csv(self):
        p=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if p:
            with open(p,"w",newline="",encoding="utf-8-sig") as f:
                w=csv.writer(f,delimiter=";");w.writerow(["Tipo","ID / ligação","Componente","Pressão (bar)","Temperatura (°C)","Entalpia (kJ/kg)","Vazão (kg/s)","Potência térmica (MW)"])
                for i,n in self.nodes.items():v=n['v'];w.writerow(["Equipamento",i,n['kind'],*v[:3],v[3],v[2]*v[3]/1000])
                for a,b in self.edges:
                    s=self.streams[f"{a}:{b}"];w.writerow(["Corrente",f"{a} → {b}","",s['p'],s['t'],s['h'],s['m'],s['m']*s['h']/1000])
            self.status.set("Tabela de componentes exportada em CSV.")

if __name__=="__main__":
    root=tk.Tk();app=ThermalEditor(root);root.mainloop()
