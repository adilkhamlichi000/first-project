import hmac
from pathlib import Path

import streamlit as st


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


# Bibliothèque cohérente : chaque mouvement pointe vers un clip local montrant
# exactement le même coach virtuel. Aucun lien YouTube ou vidéo externe.
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


def show_exercise_video(name: str, seconds: int):
    st.subheader("🎥 Suis le coach")
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

st.caption("Version 4 — bibliothèque vidéo locale préparée pour un coach virtuel unique.")
