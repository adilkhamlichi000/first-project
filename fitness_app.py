import hmac
from pathlib import Path

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


# Bibliothèque cohérente : chaque mouvement pointera à terme vers un clip local
# montrant exactement le même coach virtuel. Aucun lien YouTube ou vidéo externe.
EXERCISE_VIDEOS = {
    "Step touch": "videos/step_touch.mp4",
    "Cercles de bras": "videos/arm_circles.mp4",
    "Montées de genoux douces": "videos/gentle_high_knees.mp4",
    "Squats": "videos/squats.mp4",
    "Pompes inclinées": "videos/incline_pushups.mp4",
    "Fentes arrière": "videos/reverse_lunges.mp4",
    "Pont fessier": "videos/glute_bridge.mp4",
    "Planche": "videos/plank.mp4",
    "Bird-dog": "videos/bird_dog.mp4",
    "Jumping jacks doux": "videos/gentle_jumping_jacks.mp4",
    "Mountain climbers lents": "videos/slow_mountain_climbers.mp4",
    "Shadow boxing": "videos/shadow_boxing.mp4",
    "Cat-cow": "videos/cat_cow.mp4",
    "Rotation thoracique": "videos/thoracic_rotation.mp4",
    "Étirement des hanches": "videos/hip_flexor_stretch.mp4",
    "Étirement des ischios": "videos/hamstring_stretch.mp4",
    "Développé épaules avec haltères": "videos/dumbbell_shoulder_press.mp4",
    "Rowing avec haltères": "videos/dumbbell_row.mp4",
    "Respiration lente": "videos/slow_breathing.mp4",
    "Étirement doux": "videos/gentle_full_body_stretch.mp4",
}


# nom, consigne, durée de base en secondes
EXERCISES = {
    "Échauffement": [
        ("Step touch", "Pas à droite puis à gauche, bras actifs.", 40),
        ("Cercles de bras", "Petits puis grands cercles, épaules relâchées.", 30),
        ("Montées de genoux douces", "Reste droit et garde un rythme confortable.", 30),
    ],
    "Renforcement": [
        ("Squats", "Pieds largeur d’épaules, hanches vers l’arrière, poitrine haute.", 40),
        ("Pompes inclinées", "Mains sur une table ou un canapé, corps gainé.", 35),
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
        ("Rotation thoracique", "À quatre pattes, ouvre le coude vers le plafond sans tourner les hanches.", 40),
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


def render_squat_coach(seconds: int = 40):
    """Premier coach cohérent : animation temps réel du squat, sans source externe."""
    html = f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
      <div style="background:#f5f3ee;border-radius:22px;padding:12px 12px 8px 12px;overflow:hidden;">
        <canvas id="coach" width="420" height="520" style="width:100%;max-width:420px;display:block;margin:auto;"></canvas>
        <div style="text-align:center;font-weight:700;font-size:18px;margin-top:2px;">SQUAT • {seconds} SEC</div>
        <div style="text-align:center;color:#666;font-size:13px;margin:4px 0 8px;">Poitrine haute • genoux dans l'axe • hanches vers l'arrière</div>
      </div>
    </div>
    <script>
      const c = document.getElementById('coach');
      const ctx = c.getContext('2d');

      function mix(a,b,t) {{ return a + (b-a)*t; }}
      function pt(a,b,t) {{ return {{x:mix(a.x,b.x,t), y:mix(a.y,b.y,t)}}; }}
      function line(a,b,w,color) {{
        ctx.strokeStyle=color; ctx.lineWidth=w; ctx.lineCap='round';
        ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
      }}
      function circle(p,r,fill,stroke=null,w=2) {{
        ctx.beginPath(); ctx.arc(p.x,p.y,r,0,Math.PI*2); ctx.fillStyle=fill; ctx.fill();
        if(stroke) {{ ctx.strokeStyle=stroke; ctx.lineWidth=w; ctx.stroke(); }}
      }}

      const stand = {{
        head:{{x:210,y:82}}, neck:{{x:210,y:120}}, shoulderL:{{x:174,y:136}}, shoulderR:{{x:246,y:136}},
        elbowL:{{x:168,y:190}}, elbowR:{{x:252,y:190}}, wristL:{{x:176,y:238}}, wristR:{{x:244,y:238}},
        hipL:{{x:190,y:258}}, hipR:{{x:230,y:258}}, kneeL:{{x:188,y:350}}, kneeR:{{x:232,y:350}},
        ankleL:{{x:184,y:446}}, ankleR:{{x:236,y:446}}, toeL:{{x:164,y:462}}, toeR:{{x:256,y:462}}
      }};
      const squat = {{
        head:{{x:214,y:145}}, neck:{{x:208,y:178}}, shoulderL:{{x:171,y:190}}, shoulderR:{{x:245,y:190}},
        elbowL:{{x:204,y:218}}, elbowR:{{x:278,y:218}}, wristL:{{x:242,y:229}}, wristR:{{x:314,y:229}},
        hipL:{{x:190,y:302}}, hipR:{{x:232,y:302}}, kneeL:{{x:151,y:363}}, kneeR:{{x:273,y:363}},
        ankleL:{{x:178,y:446}}, ankleR:{{x:244,y:446}}, toeL:{{x:154,y:462}}, toeR:{{x:270,y:462}}
      }};

      function drawPose(t) {{
        ctx.clearRect(0,0,c.width,c.height);
        // studio floor + shadow
        ctx.fillStyle='#f5f3ee'; ctx.fillRect(0,0,c.width,c.height);
        ctx.strokeStyle='#d7d2c8'; ctx.lineWidth=2; ctx.beginPath(); ctx.moveTo(35,466); ctx.lineTo(385,466); ctx.stroke();
        ctx.fillStyle='rgba(0,0,0,0.08)'; ctx.beginPath(); ctx.ellipse(212,464,88,13,0,0,Math.PI*2); ctx.fill();

        const p={{}}; for(const k in stand) p[k]=pt(stand[k],squat[k],t);
        const hip={{x:(p.hipL.x+p.hipR.x)/2,y:(p.hipL.y+p.hipR.y)/2}};
        const shoulders={{x:(p.shoulderL.x+p.shoulderR.x)/2,y:(p.shoulderL.y+p.shoulderR.y)/2}};

        // hair behind head
        circle({{x:p.head.x-3,y:p.head.y+2}},27,'#3c2b24');
        // legs: black leggings
        line(p.hipL,p.kneeL,22,'#171717'); line(p.kneeL,p.ankleL,19,'#171717');
        line(p.hipR,p.kneeR,22,'#171717'); line(p.kneeR,p.ankleR,19,'#171717');
        // shoes
        line(p.ankleL,p.toeL,13,'#ffffff'); line(p.ankleR,p.toeR,13,'#ffffff');
        line(p.ankleL,p.toeL,2,'#b7b7b7'); line(p.ankleR,p.toeR,2,'#b7b7b7');
        // torso black fitted top
        ctx.fillStyle='#111111'; ctx.beginPath();
        ctx.moveTo(p.shoulderL.x,p.shoulderL.y); ctx.lineTo(p.shoulderR.x,p.shoulderR.y);
        ctx.lineTo(p.hipR.x+4,p.hipR.y); ctx.lineTo(p.hipL.x-4,p.hipL.y); ctx.closePath(); ctx.fill();
        // arms skin tone
        line(p.shoulderL,p.elbowL,14,'#c98f72'); line(p.elbowL,p.wristL,13,'#c98f72');
        line(p.shoulderR,p.elbowR,14,'#c98f72'); line(p.elbowR,p.wristR,13,'#c98f72');
        circle(p.wristL,8,'#c98f72'); circle(p.wristR,8,'#c98f72');
        // neck + face
        line(shoulders,p.neck,13,'#c98f72');
        circle(p.head,23,'#c98f72');
        // hair bun
        circle({{x:p.head.x-18,y:p.head.y-18}},10,'#3c2b24');
        // face minimal
        circle({{x:p.head.x+7,y:p.head.y-3}},2.2,'#2b211e');
        ctx.strokeStyle='#6e4438';ctx.lineWidth=2;ctx.beginPath();ctx.arc(p.head.x+8,p.head.y+7,6,0.1,1.15);ctx.stroke();

        // technique guides
        ctx.font='600 13px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif';
        ctx.fillStyle='#595959'; ctx.fillText('Hanches en arrière',22,295);
        ctx.strokeStyle='#8a8a8a';ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(132,290);ctx.lineTo(p.hipL.x-13,p.hipL.y-4);ctx.stroke();
      }}

      let start=performance.now();
      function frame(now) {{
        const cycle=((now-start)%3200)/3200;
        // 0 standing -> 1 squat -> 0 standing, with smooth easing
        let raw=(1-Math.cos(cycle*Math.PI*2))/2;
        let t=raw*raw*(3-2*raw);
        drawPose(t);
        requestAnimationFrame(frame);
      }}
      requestAnimationFrame(frame);
    </script>
    """
    components.html(html, height=590)


def show_exercise_video(name: str, seconds: int):
    st.subheader("🎥 Suis le coach")

    # Premier mouvement construit avec notre mannequin unique.
    if name == "Squats":
        st.caption("Prototype du coach unique : même personnage et même studio pour toute la future bibliothèque.")
        render_squat_coach(seconds)
        return

    video_path = Path(EXERCISE_VIDEOS[name])
    if video_path.exists():
        st.caption(
            f"Même coach virtuel pour tous les mouvements. Le clip tourne en boucle pendant tes {seconds} secondes."
        )
        st.video(
            str(video_path),
            loop=True,
            autoplay=True,
            muted=True,
            width="stretch",
        )
    else:
        st.info(
            "Le clip cohérent de ce mouvement n’est pas encore installé. "
            f"Fichier attendu : `{video_path}`"
        )


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
st.caption("Un coach vidéo cohérent directement dans ton téléphone")

if not check_password():
    st.stop()

with st.expander("⚠️ Sécurité", expanded=False):
    st.write(
        "Fais les mouvements dans une amplitude confortable. Arrête-toi en cas de douleur, malaise, "
        "essoufflement inhabituel ou vertiges. Cette app ne remplace pas un avis médical ou un coach qualifié."
    )

with st.expander("👩‍🏫 Tester notre coach unique", expanded=False):
    st.write("Premier prototype : squat. Le même mannequin sera réutilisé pour tous les mouvements.")
    render_squat_coach(40)

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

    show_exercise_video(name, seconds)

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

st.caption("Version 5 — premier mannequin animé cohérent intégré directement dans l’app.")
