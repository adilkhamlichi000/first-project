import hmac
import json

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Fitness Coach", page_icon="💪", layout="centered")


def check_password() -> bool:
    expected = st.secrets.get("APP_PASSWORD", "")
    if not expected:
        return True

    entered = st.text_input("Mot de passe", type="password")
    if not entered:
        return False
    if hmac.compare_digest(entered, expected):
        return True
    st.error("Mot de passe incorrect.")
    return False


# nom, consigne, durée de base en secondes
EXERCISES = {
    "Échauffement": [
        ("Step touch", "Pas à droite puis à gauche, bras actifs.", 40),
        ("Cercles de bras", "Petits puis grands cercles, épaules relâchées.", 30),
        ("Montées de genoux douces", "Reste droit et garde un rythme confortable.", 30),
    ],
    "Renforcement": [
        ("Squats", "Pieds largeur d’épaules, hanches vers l’arrière, poitrine haute.", 40),
        ("Pompes inclinées", "Mains sur un support stable, corps gainé.", 35),
        ("Fentes arrière", "Recule une jambe, descends doucement et alterne les côtés.", 40),
        ("Pont fessier", "Allongé sur le dos, pousse les hanches vers le haut.", 40),
        ("Planche", "Corps aligné, abdos serrés, respire normalement.", 30),
        ("Bird-dog", "À quatre pattes, tends bras et jambe opposés en alternance.", 40),
    ],
    "Cardio": [
        ("Step touch", "Pas à droite puis à gauche, bras actifs.", 45),
        ("Jumping jacks doux", "Sans saut si besoin : ouvre une jambe à la fois.", 35),
        ("Mountain climbers lents", "Mains au sol ou sur un support, genoux alternés.", 35),
        ("Shadow boxing", "Petits coups de poing contrôlés, buste gainé.", 45),
    ],
    "Mobilité": [
        ("Cat-cow", "À quatre pattes, alterne dos rond et dos creux doucement.", 45),
        ("Rotation thoracique", "À quatre pattes, ouvre un bras vers le plafond sans tourner les hanches.", 40),
        ("Étirement des hanches", "Fente légère, bassin vers l’avant sans forcer.", 40),
        ("Étirement des ischios", "Jambe légèrement tendue, dos long, sans rebond.", 40),
    ],
}


def adjusted_seconds(base_seconds: int, level: str) -> int:
    if level == "Débutant":
        return max(20, base_seconds - 5)
    if level == "Avancé":
        return base_seconds + 10
    return base_seconds


def render_virtual_coach(name: str, seconds: int):
    """Même mannequin animé pour tous les mouvements, sans vidéo externe."""
    movement_js = json.dumps(name)
    seconds_js = int(seconds)

    html = f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
      <div style="background:#f5f3ee;border-radius:22px;padding:10px;overflow:hidden;">
        <canvas id="coach" width="420" height="520" style="width:100%;max-width:420px;display:block;margin:auto"></canvas>
        <div id="label" style="text-align:center;font-weight:800;font-size:18px;color:#181818;margin-top:2px"></div>
        <div style="text-align:center;color:#666;font-size:13px;margin:4px 0 8px">Même coach • même tenue • même studio</div>
      </div>
    </div>
    <script>
    const movement = {movement_js};
    const seconds = {seconds_js};
    const c = document.getElementById('coach');
    const ctx = c.getContext('2d');
    document.getElementById('label').textContent = movement.toUpperCase() + ' • ' + seconds + ' SEC';

    const SKIN='#c98f72', HAIR='#3c2b24', TOP='#111111', LEGGINGS='#171717', SHOE='#ffffff';
    const base={{
      head:[210,82], neck:[210,120], sl:[174,138], sr:[246,138],
      el:[166,194], er:[254,194], wl:[168,246], wr:[252,246],
      hl:[190,260], hr:[230,260], kl:[188,354], kr:[232,354],
      al:[184,445], ar:[236,445], tl:[162,462], tr:[258,462]
    }};

    function clone(p){{const q={{}};for(const k in p)q[k]=[p[k][0],p[k][1]];return q;}}
    function mix(a,b,t){{return a+(b-a)*t;}}
    function interp(a,b,t){{const q={{}};for(const k in a)q[k]=[mix(a[k][0],b[k][0],t),mix(a[k][1],b[k][1],t)];return q;}}
    function line(a,b,w,col){{ctx.strokeStyle=col;ctx.lineWidth=w;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();}}
    function circ(p,r,fill,stroke=null,w=2){{ctx.beginPath();ctx.arc(p[0],p[1],r,0,Math.PI*2);ctx.fillStyle=fill;ctx.fill();if(stroke){{ctx.strokeStyle=stroke;ctx.lineWidth=w;ctx.stroke();}}}}
    function mid(a,b){{return [(a[0]+b[0])/2,(a[1]+b[1])/2];}}

    function groundPose(){{
      return {{head:[330,300],neck:[307,310],sl:[278,310],sr:[294,325],el:[240,350],er:[260,365],wl:[200,390],wr:[220,405],hl:[205,345],hr:[220,360],kl:[145,405],kr:[165,420],al:[85,430],ar:[105,445],tl:[65,437],tr:[85,452]}};
    }}

    function pose(name,u){{
      let p=clone(base); const alt=Math.sin(u*Math.PI*2); const open=(1-Math.cos(u*Math.PI*2))/2;

      if(name==='Step touch'){{
        const dx=alt*24; for(const k in p)p[k][0]+=dx;
        p.tl[0]-=28*open; p.tr[0]+=28*(1-open);
        p.wl[0]-=20*alt; p.wr[0]-=20*alt;
      }}
      else if(name==='Cercles de bras'){{
        const a=u*Math.PI*2;
        p.el=[p.sl[0]+38*Math.cos(a),p.sl[1]+38*Math.sin(a)];
        p.wl=[p.sl[0]+78*Math.cos(a),p.sl[1]+78*Math.sin(a)];
        p.er=[p.sr[0]+38*Math.cos(a+Math.PI),p.sr[1]+38*Math.sin(a+Math.PI)];
        p.wr=[p.sr[0]+78*Math.cos(a+Math.PI),p.sr[1]+78*Math.sin(a+Math.PI)];
      }}
      else if(name==='Montées de genoux douces'){{
        if(alt>=0){{p.kl=[185,300];p.al=[185,348];}} else {{p.kr=[235,300];p.ar=[235,348];}}
        p.wl[1]-=18*alt; p.wr[1]+=18*alt;
      }}
      else if(name==='Squats'){{
        const q=clone(base); q.head=[214,145];q.neck=[208,178];q.sl=[171,190];q.sr=[245,190];
        q.el=[204,218];q.er=[278,218];q.wl=[242,229];q.wr=[314,229];
        q.hl=[190,302];q.hr=[232,302];q.kl=[151,363];q.kr=[273,363];q.al=[178,445];q.ar=[244,445];q.tl=[154,462];q.tr=[270,462];
        p=interp(base,q,open);
      }}
      else if(name==='Pompes inclinées'){{
        const a={{head:[300,170],neck:[275,184],sl:[248,195],sr:[260,210],el:[220,250],er:[230,265],wl:[190,305],wr:[200,320],hl:[190,280],hr:[205,294],kl:[145,350],kr:[160,364],al:[95,420],ar:[110,434],tl:[72,438],tr:[87,452]}};
        const b=clone(a); b.head[1]+=18;b.neck[1]+=18;b.sl[1]+=20;b.sr[1]+=20;b.el[1]+=8;b.er[1]+=8;
        p=interp(a,b,open);
      }}
      else if(name==='Fentes arrière'){{
        p.kl=[180,345];p.al=[178,445];p.kr=[255,375];p.ar=[305,445];p.tr=[330,458];p.hr=[232,275];p.hl=[190,275];
        if(alt<0){{const swap=['kl','kr','al','ar','tl','tr']; const q=clone(p);p.kl=[240,345];p.al=[242,445];p.kr=[165,375];p.ar=[115,445];p.tl=[265,458];p.tr=[90,458];}}
        p.head[1]+=18*open;p.sl[1]+=15*open;p.sr[1]+=15*open;p.hl[1]+=18*open;p.hr[1]+=18*open;
      }}
      else if(name==='Pont fessier'){{
        const a={{head:[92,360],neck:[120,350],sl:[145,350],sr:[155,365],el:[125,395],er:[140,408],wl:[100,425],wr:[115,437],hl:[230,390],hr:[240,405],kl:[300,375],kr:[310,390],al:[355,432],ar:[365,446],tl:[375,438],tr:[385,452]}};
        const b=clone(a);b.hl[1]=325;b.hr[1]=340;b.sl[1]=338;b.sr[1]=352;
        p=interp(a,b,open);
      }}
      else if(name==='Planche'){{
        p=groundPose(); const dy=Math.sin(u*Math.PI*2)*3;for(const k in p)p[k][1]+=dy;
      }}
      else if(name==='Bird-dog'){{
        const a={{head:[292,300],neck:[270,315],sl:[245,325],sr:[258,338],el:[210,370],er:[220,382],wl:[175,420],wr:[185,432],hl:[210,355],hr:[225,370],kl:[165,410],kr:[270,410],al:[130,440],ar:[300,440],tl:[112,447],tr:[320,447]}};
        const b=clone(a);b.wl=[95,315];b.el=[155,325];b.ar=[360,350];b.kr=[290,365];
        p=interp(a,b,open);
      }}
      else if(name==='Jumping jacks doux'){{
        p.tl=[135+35*(1-open),462];p.tr=[285-35*(1-open),462];
        p.el=[145,175-55*open];p.wl=[125,230-150*open];p.er=[275,175-55*open];p.wr=[295,230-150*open];
      }}
      else if(name==='Mountain climbers lents'){{
        p=groundPose(); if(alt>=0){{p.kl=[205,365];p.al=[180,410];}} else {{p.kr=[220,380];p.ar=[195,425];}}
      }}
      else if(name==='Shadow boxing'){{
        if(alt>=0){{p.el=[205,175];p.wl=[310,175];p.er=[240,175];p.wr=[220,205];}} else {{p.er=[215,175];p.wr=[110,175];p.el=[180,175];p.wl=[200,205];}}
        p.head[0]+=8*alt;
      }}
      else if(name==='Cat-cow'){{
        const a={{head:[295,320],neck:[270,330],sl:[245,340],sr:[258,352],el:[215,380],er:[225,392],wl:[190,430],wr:[200,442],hl:[190,355],hr:[205,370],kl:[150,410],kr:[250,410],al:[120,445],ar:[280,445],tl:[100,452],tr:[300,452]}};
        const b=clone(a);b.head[1]=285;b.neck[1]=310;b.sl[1]=320;b.sr[1]=332;b.hl[1]=385;b.hr[1]=400;
        p=interp(a,b,open);
      }}
      else if(name==='Rotation thoracique'){{
        p={{head:[280,315],neck:[258,328],sl:[235,340],sr:[248,352],el:[205,385],er:[270,300],wl:[185,430],wr:[300,245],hl:[190,355],hr:[205,370],kl:[150,410],kr:[250,410],al:[120,445],ar:[280,445],tl:[100,452],tr:[300,452]}};
        p.wr[1]+=90*(1-open);p.er[1]+=60*(1-open);
      }}
      else if(name==='Étirement des hanches'){{
        p.kl=[180,340];p.al=[175,445];p.kr=[265,395];p.ar=[315,445];p.tr=[340,458];p.head[1]+=8*open;p.hl[1]+=8*open;p.hr[1]+=8*open;
      }}
      else if(name==='Étirement des ischios'){{
        p.kl=[185,360];p.al=[180,445];p.kr=[265,360];p.ar=[325,445];p.tr=[350,458];
        p.head=[245,175+45*open];p.neck=[230,205+45*open];p.sl=[195,220+35*open];p.sr=[255,220+35*open];p.el=[230,275+35*open];p.er=[285,275+35*open];p.wl=[275,335+35*open];p.wr=[325,335+35*open];
      }}
      else if(name==='Développé épaules avec haltères'){{
        p.el=[175,195-45*open];p.er=[245,195-45*open];p.wl=[175,245-145*open];p.wr=[245,245-145*open];
      }}
      else if(name==='Rowing avec haltères'){{
        p.head=[245,160];p.neck=[225,190];p.sl=[190,205];p.sr=[250,205];p.hl=[185,285];p.hr=[225,285];
        p.el=[165,275-45*open];p.er=[260,275-45*open];p.wl=[160,335-70*open];p.wr=[270,335-70*open];
      }}
      else if(name==='Respiration lente'){{
        p.wl=[150,250-130*open];p.wr=[270,250-130*open];p.el=[160,200-80*open];p.er=[260,200-80*open];
      }}
      else if(name==='Étirement doux'){{
        const bend=alt*22; for(const k of ['head','neck','sl','sr','el','er','wl','wr'])p[k][0]+=bend;
        p.wl=[170+bend,115];p.wr=[250+bend,115];p.el=[175+bend,160];p.er=[245+bend,160];
      }}
      return p;
    }}

    function draw(p){{
      ctx.clearRect(0,0,c.width,c.height);ctx.fillStyle='#f5f3ee';ctx.fillRect(0,0,c.width,c.height);
      ctx.strokeStyle='#d5d0c6';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(30,466);ctx.lineTo(390,466);ctx.stroke();
      ctx.fillStyle='rgba(0,0,0,.08)';ctx.beginPath();ctx.ellipse(210,463,90,12,0,0,Math.PI*2);ctx.fill();

      // jambes
      line(p.hl,p.kl,22,LEGGINGS);line(p.kl,p.al,19,LEGGINGS);line(p.hr,p.kr,22,LEGGINGS);line(p.kr,p.ar,19,LEGGINGS);
      line(p.al,p.tl,13,SHOE);line(p.ar,p.tr,13,SHOE);line(p.al,p.tl,2,'#aaa');line(p.ar,p.tr,2,'#aaa');

      // torse
      ctx.fillStyle=TOP;ctx.beginPath();ctx.moveTo(p.sl[0],p.sl[1]);ctx.lineTo(p.sr[0],p.sr[1]);ctx.lineTo(p.hr[0]+4,p.hr[1]);ctx.lineTo(p.hl[0]-4,p.hl[1]);ctx.closePath();ctx.fill();

      // bras
      line(p.sl,p.el,14,SKIN);line(p.el,p.wl,13,SKIN);line(p.sr,p.er,14,SKIN);line(p.er,p.wr,13,SKIN);circ(p.wl,7,SKIN);circ(p.wr,7,SKIN);

      // haltères si besoin
      if(movement==='Développé épaules avec haltères'||movement==='Rowing avec haltères'){{line([p.wl[0]-10,p.wl[1]],[p.wl[0]+10,p.wl[1]],7,'#555');line([p.wr[0]-10,p.wr[1]],[p.wr[0]+10,p.wr[1]],7,'#555');}}

      // tête / cheveux / cou
      const sh=mid(p.sl,p.sr);line(sh,p.neck,13,SKIN);circ([p.head[0]-3,p.head[1]+2],27,HAIR);circ(p.head,23,SKIN);circ([p.head[0]-18,p.head[1]-18],10,HAIR);circ([p.head[0]+7,p.head[1]-3],2.2,'#2b211e');
      ctx.strokeStyle='#6e4438';ctx.lineWidth=2;ctx.beginPath();ctx.arc(p.head[0]+8,p.head[1]+7,6,.1,1.15);ctx.stroke();
    }}

    const start=performance.now();
    function frame(now){{const u=((now-start)%3200)/3200;draw(pose(movement,u));requestAnimationFrame(frame);}}
    requestAnimationFrame(frame);
    </script>
    """
    components.html(html, height=590)


def build_session(goal: str, duration: int, level: str, equipment: str):
    session = []
    session.extend(EXERCISES["Échauffement"])

    if goal == "Se muscler":
        pool = EXERCISES["Renforcement"]
    elif goal == "Cardio / brûler des calories":
        pool = EXERCISES["Cardio"] + EXERCISES["Renforcement"][:2]
    elif goal == "Mobilité / récupération":
        pool = EXERCISES["Mobilité"]
    else:
        pool = EXERCISES["Renforcement"][:3] + EXERCISES["Cardio"][:2]

    if equipment == "Haltères légers":
        pool = pool + [
            ("Développé épaules avec haltères", "Pousse les haltères au-dessus de la tête sans cambrer.", 35),
            ("Rowing avec haltères", "Buste légèrement penché, tire les coudes vers l’arrière.", 40),
        ]

    rounds = 1 if duration <= 15 else 2 if duration <= 30 else 3
    if level == "Débutant":
        rounds = max(1, rounds - 1)
    elif level == "Avancé":
        rounds += 1

    for _ in range(rounds):
        session.extend(pool)

    session.extend([
        ("Respiration lente", "Inspire 4 secondes, expire 6 secondes.", 60),
        ("Étirement doux", "Relâche jambes, dos et épaules sans forcer.", 60),
    ])

    return [
        (name, instruction, adjusted_seconds(seconds, level))
        for name, instruction, seconds in session
    ]


st.title("💪 Fitness Coach")
st.caption("Un seul coach animé pour toute ta séance")

if not check_password():
    st.stop()

with st.expander("⚠️ Sécurité", expanded=False):
    st.write(
        "Les animations sont des guides visuels simplifiés. Fais les mouvements dans une amplitude confortable. "
        "Arrête-toi en cas de douleur, malaise, essoufflement inhabituel ou vertiges."
    )

st.subheader("Créer ma séance")
goal = st.selectbox(
    "Objectif",
    ["Forme générale", "Se muscler", "Cardio / brûler des calories", "Mobilité / récupération"],
)
level = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé"])
duration = st.select_slider("Durée", options=[10, 15, 20, 30, 45], value=20, format_func=lambda x: f"{x} min")
equipment = st.selectbox("Matériel", ["Aucun", "Haltères légers"])

if st.button("Créer la séance", type="primary", use_container_width=True):
    st.session_state["workout"] = build_session(goal, duration, level, equipment)
    st.session_state["exercise_index"] = 0
    st.session_state["workout_meta"] = {
        "goal": goal,
        "duration": duration,
        "level": level,
        "equipment": equipment,
    }

workout = st.session_state.get("workout")

if workout:
    idx = min(st.session_state.get("exercise_index", 0), len(workout) - 1)
    name, instruction, seconds = workout[idx]
    meta = st.session_state.get("workout_meta", {})

    st.divider()
    st.caption(
        f"{meta.get('goal', '')} • {meta.get('duration', '')} min • {meta.get('level', '')} • {meta.get('equipment', '')}"
    )
    st.progress((idx + 1) / len(workout))
    st.write(f"Exercice {idx + 1} sur {len(workout)}")
    st.header(name)
    st.metric("Durée", f"{seconds} sec")
    st.info(instruction)

    st.subheader("🎥 Suis le coach")
    render_virtual_coach(name, seconds)
    st.write(f"⏱️ Fais le mouvement pendant **{seconds} secondes**, puis passe au suivant.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Précédent", use_container_width=True, disabled=idx == 0):
            st.session_state["exercise_index"] = idx - 1
            st.rerun()
    with col2:
        if idx < len(workout) - 1:
            if st.button("Suivant ➡️", type="primary", use_container_width=True):
                st.session_state["exercise_index"] = idx + 1
                st.rerun()
        else:
            if st.button("✅ Terminer", type="primary", use_container_width=True):
                st.success("Séance terminée. Bravo !")
                st.balloons()

    if st.button("🔄 Recommencer cette séance", use_container_width=True):
        st.session_state["exercise_index"] = 0
        st.rerun()

st.caption("Version 6 — même mannequin animé pour chaque mouvement, sans YouTube ni fichier vidéo externe.")
