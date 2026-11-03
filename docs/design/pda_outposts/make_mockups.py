# Renders the three PDA Outposts layout mockups (design only, not game code).
# Frame = the PDA window as in ui_stalker_camp_builder_pda.xml (764x603), drawn at S x.
from PIL import Image, ImageDraw, ImageFont
import os
S = 1.5
OUT = os.path.dirname(os.path.abspath(__file__))
FD = "C:/Windows/Fonts/"
def F(sz, b=False): return ImageFont.truetype(FD + ("calibrib.ttf" if b else "calibri.ttf"), int(sz * S))
BG=(24,28,33); PANEL=(31,37,44); HDR=(44,52,62); LINE=(58,68,80)
GOLD=(228,186,84); GOLDBG=(86,76,38); TXT=(214,220,226); DIM=(130,140,150)
GOOD=(122,224,138); GOODBG=(26,60,34); WARN=(236,176,70); BAD=(232,96,90); BADBG=(70,28,28)
GREY=(120,128,136); GREYBG=(48,52,58)

SAMPLE = [  # name, level, tier, faction, state
 ("Cordon Farm Camp","Cordon",1,"Loners","friendly"),
 ("Army Warehouses Fort","Army Warehouses",3,"Bandits","hostile"),
 ("Yantar Swamp Nest","Yantar",2,"Mutants","hostile"),
 ("Rostok Yard Post","Rostok",2,"-","abandoned"),
 ("Garbage Depot","Garbage",1,"Clear Sky","friendly"),
 ("Agroprom Mill","Agroprom",2,"Duty","friendly"),
 ("Dark Valley Bunker","Dark Valley",3,"Freedom","hostile"),
]
ST = {"friendly":(GOOD,GOODBG,"ALLIED CONTROL // SECURED"),
      "hostile":(BAD,BADBG,"THREAT IDENTIFIED // HOSTILE"),
      "abandoned":(GREY,GREYBG,"ABANDONED OUTPOST // UNCLAIMED")}
INTEL = ("Old military supply depot. Lookouts on the roofs, a machine-gun nest on the "
         "north gate. Expect heavy resistance; the south fence is thin.")

class C:
    def __init__(s, title):
        s.im = Image.new("RGB",(int(764*S),int(640*S)),(12,14,17)); s.d = ImageDraw.Draw(s.im); s.title=title
    def r(s,x,y,w,h,fill=None,outline=None):
        s.d.rectangle([x*S,y*S,(x+w)*S,(y+h)*S],fill=fill,outline=outline)
    def t(s,x,y,txt,sz=14,col=TXT,b=False,a="l",w=0):
        f=F(sz,b); tw=s.d.textlength(txt,font=f)
        px = x*S if a=="l" else (x+w/2)*S-tw/2 if a=="c" else (x+w)*S-tw
        s.d.text((px,y*S),txt,font=f,fill=col)
    def frame(s, active=2):
        s.r(0,0,764,603,BG,LINE)
        s.r(6,6,152,268,PANEL,LINE)
        for i,n in enumerate(["Overview","Survivors","Outposts","Radio","Guide"]):
            y=10+i*42; on=(i==active)
            s.r(6,y,148,36,GOLDBG if on else HDR,GOLD if on else LINE)
            s.t(6,y+8,n,16,GOLD if on else DIM,on,"c",148)
        s.r(184,2,564,24,HDR,LINE)
        s.t(190,5,"SIGNAL 4/5",12,DIM); s.t(330,5,"CLEAR  14:32",12,DIM); s.t(560,5,"Camp: Army Warehouses",12,DIM)
    def banner(s,x,y,w,state,label=None,h=24):
        c,bg,lbl=ST[state]; s.r(x,y,w,h,bg,c); s.t(x,y+3,"[ "+(label or lbl)+" ]",13,c,True,"c",w)
    def module(s,x,y,w,h,title):
        s.r(x,y,w,h,PANEL,LINE); s.r(x,y,w,20,HDR); s.t(x+8,y+2,title.upper(),13,TXT,True)
    def row(s,x,y,k,v,col=TXT,w=340):
        s.t(x+8,y,k,13,DIM); s.t(x+w*0.38,y,v,13,col,True)
    def btn(s,x,y,w,h,txt,col=TXT):
        s.r(x,y,w,h,HDR,LINE); s.t(x,y+(h-18)/2,txt,14,col,False,"c",w)
    def pill(s,x,y,txt,col,bg=None,w=None):
        f=F(11,True); tw=s.d.textlength(txt,font=f)/S+10
        s.r(x,y,w or tw,15,bg or PANEL,col); s.t(x,y,txt,11,col,True,"c",w or tw)
    def save(s,name):
        s.t(6,610,s.title,15,GOLD,True); s.im.save(os.path.join(OUT,name)); return s.im

def thumb(c,x,y,w,h,level,col=(60,72,64)):
    c.r(x,y,w,h,col,LINE)
    for i in range(0,int(w),12): c.d.line([(x+i)*S,(y+h)*S,(x+i+h*0.4)*S,y*S],fill=tuple(max(0,v-12) for v in col),width=1)
    c.t(x,y+h/2-8,level.upper(),12,(190,200,190),True,"c",w)

def intel(c,x,y,w,h=70):
    c.module(x,y,w,h,"Intel")
    line="";yy=y+24
    for wd in INTEL.split():
        if c.d.textlength(line+wd,font=F(13))/S>w-16: c.t(x+8,yy,line,13,TXT); yy+=16; line=""
        line+=wd+" "
    c.t(x+8,yy,line,13,TXT)

def conceptA():
    c=C("A  Compact list + dossier  (every row shows hostility; ~9 outposts visible instead of 5)"); c.frame()
    c.r(184,30,180,24,HDR,LINE); c.t(184,33,"OUTPOSTS (7)",14,GOLD,True,"c",180)
    c.r(184,56,180,510,PANEL,LINE)
    for i,(n,lv,tr,fa,stt) in enumerate(SAMPLE):
        y=58+i*54; sel=(i==1); col=ST[stt][0]
        c.r(186,y,176,50,GOLDBG if sel else BG,GOLD if sel else LINE)
        c.r(186,y,5,50,col)
        c.t(196,y+3,n,13,GOLD if sel else TXT,True)
        c.t(196,y+19,f"{lv}  |  Tier {tr}",12,DIM)
        c.t(196,y+33,{"friendly":fa.upper(),"hostile":"HOSTILE "+fa.upper(),"abandoned":"ABANDONED"}[stt],11,col,True)
    x=378; w=370
    c.t(x,30,"Army Warehouses Fort",20,GOLD,True,"c",w); c.t(x,52,"Tier 3 Stronghold   |   Army Warehouses",13,DIM,False,"c",w)
    c.banner(x,74,w,"hostile")
    c.module(x,104,w,92,"Faction & Garrison")
    c.row(x,128,"Faction","Bandits",BAD,w); c.row(x,146,"Garrison","11 stalkers",TXT,w); c.row(x,164,"Status","Not cleared",BAD,w)
    c.module(x,202,w,62,"Location")
    c.row(x,226,"Region","Army Warehouses",TXT,w); c.row(x,244,"Distance","1.4 km",TXT,w)
    intel(c,x,270,w,84)
    c.btn(x,366,178,28,"Locate on Map"); c.btn(x+190,366,180,28,"Refresh")
    return c.save("concept_A_compact_list.png")

def conceptB():
    c=C("B  Hero picture + stat tiles  (map-dossier look; keeps the level photos)"); c.frame()
    c.r(184,30,180,24,HDR,LINE); c.t(184,33,"OUTPOSTS (7)",14,GOLD,True,"c",180)
    c.r(184,56,180,510,PANEL,LINE)
    for i,(n,lv,tr,fa,stt) in enumerate(SAMPLE[:5]):
        y=58+i*100; sel=(i==1); col=ST[stt][0]
        c.r(186,y,176,96,GOLDBG if sel else BG,GOLD if sel else LINE)
        thumb(c,190,y+4,168,52,lv)
        c.r(190,y+4,168,3,col)
        c.pill(194,y+10,{"friendly":"ALLY","hostile":"HOSTILE","abandoned":"EMPTY"}[stt],col,(18,20,24))
        c.t(186,y+58,n,14,GOLD,True,"c",176); c.t(186,y+76,f"{fa}  |  Tier {tr}" if fa!="-" else f"Unclaimed  |  Tier {tr}",12,DIM,False,"c",176)
    x=378; w=370
    thumb(c,x,30,w,118,"Army Warehouses",(64,70,58))
    c.r(x,30,w,4,BAD)
    c.t(x+10,98,"Army Warehouses Fort",20,GOLD,True)
    c.t(x+10,122,"Tier 3 Stronghold  |  Army Warehouses",12,TXT)
    c.pill(x+w-96,40,"HOSTILE",BAD,(18,20,24),86)
    c.banner(x,154,w,"hostile")
    for i,(k,v,col) in enumerate([("FACTION","Bandits",BAD),("GARRISON","11",TXT),("DISTANCE","1.4 km",TXT)]):
        tx=x+i*125; c.r(tx,184,120,56,PANEL,LINE); c.t(tx,188,k,11,DIM,False,"c",120); c.t(tx,206,v,20,col,True,"c",120)
    intel(c,x,248,w,100)
    c.btn(x,360,178,28,"Locate on Map"); c.btn(x+190,360,180,28,"Refresh")
    return c.save("concept_B_hero.png")

def conceptC():
    c=C("C  Sub-tabs in the panel  (same look as the chosen Overview; filter chips on the list)"); c.frame()
    c.r(184,30,180,24,HDR,LINE); c.t(184,33,"OUTPOSTS (7)",14,GOLD,True,"c",180)
    for i,(lbl,cn) in enumerate([("All",7),("Hostile",3),("Allied",3),("Empty",1)]):
        on=(i==0); bx=184+i*45
        c.r(bx,56,43,22,GOLDBG if on else HDR,GOLD if on else LINE); c.t(bx,59,lbl,12,GOLD if on else DIM,on,"c",43)
    c.r(184,80,180,486,PANEL,LINE)
    for i,(n,lv,tr,fa,stt) in enumerate(SAMPLE):
        y=82+i*50; sel=(i==1); col=ST[stt][0]
        c.r(186,y,176,46,GOLDBG if sel else BG,GOLD if sel else LINE)
        c.r(186,y,5,46,col)
        c.t(196,y+3,n,13,GOLD if sel else TXT,True); c.t(196,y+22,f"{lv}  |  Tier {tr}",12,DIM)
    x=378; w=370
    c.t(x,30,"Army Warehouses Fort",20,GOLD,True,"c",w); c.t(x,52,"Region: Army Warehouses  |  Tier 3 Stronghold",12,DIM,False,"c",w)
    for i,n in enumerate(["Intel","Garrison","Location"]):
        on=(i==0); bx=x+i*124
        c.r(bx,72,122,26,GOLDBG if on else HDR,GOLD if on else LINE); c.t(bx,76,n,14,GOLD if on else DIM,on,"c",122)
    c.banner(x,102,w,"hostile","HOSTILE  |  BANDITS  |  11 stalkers")
    intel(c,x,134,w,130)
    c.t(x+8,206,"Weak point:  south fence",13,WARN,True)
    c.t(x+8,224,"Threat level:  high",13,BAD)
    c.module(x,274,w,100,"Quick facts")
    c.row(x,298,"Faction","Bandits",BAD,w); c.row(x,316,"Garrison","11 stalkers",TXT,w); c.row(x,334,"Distance","1.4 km",TXT,w); c.row(x,352,"Status","Not cleared",BAD,w)
    c.btn(x,386,178,28,"Locate on Map"); c.btn(x+190,386,180,28,"Refresh")
    c.t(x,424,"Garrison / Location tabs show the same data in larger blocks;",11,DIM)
    c.t(x,438,"Intel is the landing tab.",11,DIM)
    return c.save("concept_C_tabs.png")

ims=[conceptA(),conceptB(),conceptC()]
W=sum(i.width for i in ims)+40; H=ims[0].height+10
sheet=Image.new("RGB",(W,H),(8,9,11)); x=10
for i in ims: sheet.paste(i,(x,5)); x+=i.width+10
sheet=sheet.resize((int(W*0.62),int(H*0.62)),Image.LANCZOS); sheet.save(os.path.join(OUT,"comparison.png"))
print(sheet.size)
