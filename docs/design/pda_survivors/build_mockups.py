# Builds the three Survivors-tab layout mockups (700x1072 = PDA panel area at 1920x1080 UI) + comparison sheet.
from PIL import Image, ImageDraw, ImageFont
import os
OUT = os.path.dirname(os.path.abspath(__file__))
F = "C:/Windows/Fonts/"
def font(sz, b=False): return ImageFont.truetype(F + ("segoeuib.ttf" if b else "segoeui.ttf"), sz)
BG=(14,17,22); PANEL=(26,31,39); HEAD=(38,44,54); BTN=(44,50,58); LINE=(62,70,82)
GOLD=(238,196,112); TXT=(200,200,200); DIM=(130,136,144); MINT=(144,238,144); BLUE=(100,200,255); RED=(255,100,100); ORG=(240,160,70)
ACT=(60,62,40)
W,H=700,1072

def T(d,xy,s,sz=18,fill=TXT,b=False,a="l"):
    d.text(xy,s,font=font(sz,b),fill=fill,anchor={"l":"lm","c":"mm","r":"rm"}[a])
def box(d,x,y,w,h,fill=PANEL,out=None): d.rectangle([x,y,x+w-1,y+h-1],fill=fill,outline=out)
def head(d,x,y,w,s,col=TXT):
    box(d,x,y,w,28,HEAD); T(d,(x+8,y+14),s.upper(),18,col,True)
def btn(d,x,y,w,h,s,on=False,col=TXT,sz=17):
    box(d,x,y,w,h,ACT if on else BTN,GOLD if on else LINE); T(d,(x+w//2,y+h//2),s,sz,GOLD if on else col,on,"c")
def bar(d,x,y,w,h,p,c):
    box(d,x,y,w,h,(8,10,13),LINE); box(d,x+1,y+1,int((w-2)*p),h-2,c)
def dot(d,x,y,c): d.ellipse([x-6,y-6,x+6,y+6],fill=c)

R=[("Sergei Volkov","Cook [Gourmet]","T1",MINT,"Hungry",ORG),
   ("Nadia Orlova","Medic [Auto]","T2",MINT,"Fed",MINT),
   ("Tikhon Rusty","Woodcutter  PAUSED","T0",ORG,"Hungry",ORG),
   ("Vasya Kuzmin","Scavenge  64% Cordon","T0",BLUE,"Fed",MINT),
   ("Dima Petrenko","Guard","T1",MINT,"Starving",RED),
   ("Lena Sokol","Resting","T0",DIM,"Fed",MINT),
   ("Boris Gromov","Craft [5.45]","T2",MINT,"Fed",MINT),
   ("Misha Zaitsev","Farmer","T0",MINT,"Hungry",ORG)]
JOBS=["Idle","Guard","Scavenge","Hunter","Craft","Repair","Cook","Medic","Electrician","Woodcutter","Brewer","Scrapper","Farmer","Trader"]

def portrait(d,x,y,s):
    box(d,x,y,s,s,(54,60,52),LINE); d.ellipse([x+s*.3,y+s*.14,x+s*.7,y+s*.54],fill=(98,104,92)); d.rectangle([x+s*.2,y+s*.6,x+s*.8,y+s-3],fill=(78,86,74))

def filters(d,x,y,w):
    names=["All","Exped.","Working","Idle"]; cw=(w-3*4)//4
    for i,n in enumerate(names): btn(d,x+i*(cw+4),y,cw,28,n,i==0,sz=15)

def dossier(d,x,y,w):
    box(d,x,y,w,86,PANEL,LINE); portrait(d,x+8,y+8,70)
    T(d,(x+90,y+22),"Sergei Volkov",22,GOLD,True); T(d,(x+90,y+48),"Rank: Skilled (Tier 1)",16,MINT)
    T(d,(x+90,y+70),"XP 142 / 250",15,BLUE); bar(d,x+190,y+63,w-206,14,142/250,BLUE)

def telemetry(d,x,y,w):
    head(d,x,y,w,"Current job",BLUE); box(d,x,y+28,w,82,PANEL,LINE)
    T(d,(x+10,y+46),"Cook [Gourmet]  -  64%  (2m 10s left)",17,TXT)
    bar(d,x+10,y+62,w-20,12,.64,MINT)
    T(d,(x+10,y+90),"Status: Cooking at Field Kitchen",16,DIM)

def needs_line(d,x,y,w):
    box(d,x,y,w,56,PANEL,LINE)
    T(d,(x+10,y+16),"Needs",16,DIM); T(d,(x+90,y+16),"HUNGRY - eats next round",16,ORG,True)
    T(d,(x+10,y+40),"Morale",16,DIM); T(d,(x+90,y+40),"72%",16,MINT,True); bar(d,x+140,y+34,w-156,12,.72,MINT)

def jobgrid(d,x,y,w,cols=2,sel="Cook",h=30,names=None):
    names=names or JOBS; cw=(w-(cols-1)*4)//cols
    for i,n in enumerate(names):
        btn(d,x+(i%cols)*(cw+4),y+(i//cols)*(h+4),cw,h,n,n==sel,sz=16)

def orders(d,x,y,w):
    h=30
    btn(d,x,y,w,h,"Station Here"); btn(d,x,y+34,w,h,"Recall to Camp"); btn(d,x,y+68,w,h,"Job Directive: Gourmet"); btn(d,x,y+102,w,h,"Rename")

def concept_A():
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    filters(d,0,0,230)
    for i,(n,j,t,jc,ns,nc) in enumerate(R):
        y=36+i*74; box(d,0,y,230,70,ACT if i==0 else PANEL,GOLD if i==0 else LINE)
        portrait(d,6,y+6,58); T(d,(72,y+18),n,17,GOLD if i==0 else TXT,True); T(d,(72,y+40),j,14,jc); T(d,(72,y+58),t+"  -  "+ns,13,nc)
    d.line([(238,0),(238,H)],fill=LINE)
    x=248; w=W-x
    dossier(d,x,0,w); telemetry(d,x,96,w)
    head(d,x,216,w,"Needs & morale",BLUE); needs_line(d,x,244,w)
    head(d,x,308,w,"Reassign job",GOLD); jobgrid(d,x,340,w,3,"Cook",30)
    jy=340+5*34+6
    head(d,x,jy,w,"Orders",BLUE); orders(d,x,jy+34,w)
    ty=jy+34+140
    head(d,x,ty,w,"Transfer to outpost",BLUE); box(d,x,ty+28,w,90,PANEL,LINE)
    for i,n in enumerate(["Cordon Outpost","Rostok Yard"]): T(d,(x+10,ty+46+i*22),n,15,GOLD if i==0 else TXT)
    btn(d,x+8,ty+120-34,w-16,26,"Transfer")
    btn(d,x,ty+128,w,30,"Banish Survivor",col=RED)
    return im

def concept_B():
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    filters(d,0,0,W)
    box(d,0,34,W,22,HEAD)
    for x,s in [(54,"NAME"),(250,"JOB"),(470,"RANK"),(540,"NEEDS")]: T(d,(x,45),s,13,DIM,True)
    for i,(n,j,t,jc,ns,nc) in enumerate(R):
        y=58+i*42; box(d,0,y,W,40,ACT if i==0 else PANEL,GOLD if i==0 else LINE)
        portrait(d,4,y+4,32); T(d,(54,y+20),n,17,GOLD if i==0 else TXT,True); T(d,(250,y+20),j,15,jc)
        T(d,(470,y+20),t,15,TXT); dot(d,548,y+20,nc); T(d,(562,y+20),ns,15,nc)
    box(d,W-6,58,6,330,(20,24,30)); box(d,W-6,58,6,260,LINE)
    y0=402
    box(d,0,y0,W,60,PANEL,LINE); portrait(d,6,y0+6,48)
    T(d,(64,y0+18),"Sergei Volkov",20,GOLD,True); T(d,(64,y0+42),"Skilled (T1)   XP 142/250",15,BLUE); bar(d,300,y0+36,W-316,12,.57,BLUE)
    tabs=["Job","Orders","Transfer","Stats"]; tw=(W-12)//4
    for i,n in enumerate(tabs): btn(d,i*(tw+4),y0+66,tw,32,n,i==0)
    box(d,0,y0+104,W,24,(10,60,30),MINT); T(d,(W//2,y0+116),"WORKING  |  Cook [Gourmet] 64%  |  Needs: Hungry",15,MINT,False,"c")
    head(d,0,y0+134,W,"Job",GOLD); box(d,0,y0+162,W,60,PANEL,LINE)
    T(d,(10,y0+180),"Cook [Gourmet]  -  2m 10s left",17); bar(d,10,y0+196,W-20,12,.64,MINT)
    head(d,0,y0+228,W,"Reassign",GOLD); jobgrid(d,0,y0+260,W,4,"Cook",30)
    T(d,(10,y0+260+4*34+14),"Other tabs: Orders (station / recall / directive / rename),  Transfer (+ banish),  Stats (needs, morale, history)",13,DIM)
    return im

def concept_C():
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    rw=170
    for i,n in enumerate(["All","Exp","Work","Idle"]): btn(d,i*43,0,40,28,n,i==0,sz=14)
    for i,(n,j,t,jc,ns,nc) in enumerate(R):
        y=34+i*60; box(d,0,y,rw,56,ACT if i==0 else PANEL,GOLD if i==0 else LINE)
        portrait(d,4,y+4,48); T(d,(58,y+16),n.split()[0],16,GOLD if i==0 else TXT,True); T(d,(58,y+38),t,14,TXT); dot(d,rw-16,y+16,nc)
    x=180; w=W-x
    dossier(d,x,0,w)
    tiles=[("RANK","Skilled",MINT),("NEEDS","Hungry",ORG),("MORALE","72%",MINT),("JOB","Cook",GOLD)]
    tw=(w-3*4)//4
    for i,(a,b,c) in enumerate(tiles):
        tx=x+i*(tw+4); box(d,tx,94,tw,62,PANEL,LINE); T(d,(tx+tw//2,110),a,13,DIM,False,"c"); T(d,(tx+tw//2,136),b,20,c,True,"c")
    telemetry(d,x,164,w)
    head(d,x,284,w,"Assign job",GOLD)
    cats=["Camp","Craft","Support","Field"]; cw=(w-12)//4
    for i,n in enumerate(cats): btn(d,x+i*(cw+4),316,cw,30,n,i==1,sz=16)
    craft=["Craft","Repair","Brewer","Cook","Scrapper","Electrician"]
    jobgrid(d,x,352,w,3,"Cook",34,craft)
    T(d,(x+2,352+2*38+12),"Camp: Idle Guard Farmer Woodcutter | Support: Medic Trader | Field: Scavenge Hunter",12,DIM)
    head(d,x,500,w,"Orders",BLUE)
    cw2=(w-4)//2
    btn(d,x,532,cw2,32,"Station Here"); btn(d,x+cw2+4,532,cw2,32,"Recall")
    btn(d,x,568,cw2,32,"Directive"); btn(d,x+cw2+4,568,cw2,32,"Rename")
    head(d,x,610,w,"Transfer",BLUE); box(d,x,638,w,70,PANEL,LINE)
    T(d,(x+10,656),"Cordon Outpost",15,GOLD); T(d,(x+10,678),"Rostok Yard",15)
    btn(d,x+w-130,648,120,50,"Transfer")
    btn(d,x,716,w,30,"Banish Survivor",col=RED)
    return im

def sheet(ims):
    caps=[("A  Split view (roster + one long detail)",
       ["+ closest to today: least rework, safest","+ whole roster beside the detail","- narrow roster rows, 3-line cards","- detail is long: jobs + orders + transfer scroll"]),
      ("B  Table roster + mini-tabs",
       ["+ full-width roster: name, job, rank, needs columns","+ same tab look as Overview (concept C)","+ detail split into Job / Orders / Transfer","- only ~7 roster rows visible; detail starts lower"]),
      ("C  Rail + tiles + job categories",
       ["+ at-a-glance tiles: rank, needs, morale, job","+ job grid cut to 6 buttons via category tabs","+ orders in a compact 2x2 block","- category tabs need extra clicks; tiny roster"])]
    g=16; capH=190; S=Image.new("RGB",(W*3+g*4,H+capH+2*g),(6,8,10)); d=ImageDraw.Draw(S)
    for i,(im,(t,l)) in enumerate(zip(ims,caps)):
        x=g+i*(W+g); S.paste(im,(x,g)); T(d,(x,g+H+22),t,22,GOLD,True)
        for k,s in enumerate(l): T(d,(x,g+H+54+k*26),s,16,MINT if s[0]=="+" else ORG)
    return S

if __name__=="__main__":
    ims=[concept_A(),concept_B(),concept_C()]
    for n,im in zip(["concept_A_split","concept_B_table_tabs","concept_C_rail_tiles"],ims): im.save(os.path.join(OUT,n+".png"))
    sheet(ims).save(os.path.join(OUT,"comparison.png"))
