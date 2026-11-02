import bpy, bmesh, numpy as np, os
TMP=__import__('os').environ.get('HSHF_TMP', r"C:\Users\hocke\AppData\Local\Temp\claude_sp")
def analyze(ob):
    me=ob.data
    img=bpy.data.images.get("atlas_wp.png") or bpy.data.images.load(os.path.join(TMP,'atlas_wp.png'))
    W,H=img.size; px=np.array(img.pixels[:]).reshape(H,W,4)
    uv=me.uv_layers[0].data
    bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    seen=set(); comps=[]
    for f in bm.faces:
        if f.index in seen: continue
        st=[f]; seen.add(f.index); cur=[]
        while st:
            x=st.pop(); cur.append(x.index)
            for e in x.edges:
                for g in e.link_faces:
                    if g.index not in seen: seen.add(g.index); st.append(g)
        comps.append(cur)
    def srgb(c): return np.where(c<=0.0031308,c*12.92,1.055*np.power(c,1/2.4)-0.055)
    info=[]
    for c in comps:
        sel=c[::max(1,len(c)//150)]
        cols=[]
        for fi in sel:
            p=me.polygons[fi]; cc=np.zeros(3)
            for li in p.loop_indices:
                u,v=uv[li].uv; cc+=px[min(H-1,int(v*H)),min(W-1,int(u*W)),:3]
            cols.append(cc/p.loop_total)
        col=srgb(np.mean(cols,axis=0))
        vs=np.array([me.vertices[v].co[:] for i in sel for v in me.polygons[i].vertices])
        info.append(dict(n=len(c),col=col,lo=vs.min(0),hi=vs.max(0),mat=me.polygons[c[0]].material_index,faces=c))
    return info
