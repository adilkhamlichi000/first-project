import hmac

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


# Chaque mouvement proposé dans l'app a maintenant une démonstration vidéo
# intégrée. Les clips tournent en boucle directement dans Streamlit.
EXERCISE_VIDEOS = {
    "Cercles de bras": "https://www.youtube.com/watch?v=2yqZn9K5f4I",
    "Montées de genoux douces": "https://www.youtube.com/watch?v=OAJ_J3EZkdY",
    "Step touch": "https://www.youtube.com/watch?v=wH9hsR7Ck_M",
    "Squats": "https://www.youtube.com/watch?v=aclHkVaku9U",
    "Pompes inclinées": "https://www.youtube.com/watch?v=Gvm5Q29UHbk",
    "Pont fessier": "https://www.youtube.com/watch?v=wPM8icPu6H8",
    "Planche": "https://www.youtube.com/watch?v=DjEN3SKl0Eg",
    "Bird-dog": "https://www.youtube.com/watch?v=ZdAHe9_HeEw",
    "Jumping jacks doux": "https://www.youtube.com/watch?v=c4DAnQ6DtF8",
    "Mountain climbers lents": "https://www.youtube.com/watch?v=nmwgirgXLYM",
    "Shadow boxing": "https://www.youtube.com/watch?v=Q1Piq_vMh5g",
    "Cat-cow": "https://www.youtube.com/watch?v=MSBOBAIeLqI",
    "Rotation thoracique": "https://www.youtube.com/watch?v=snzLuyYgbVI",
    "Étirement des hanches": "https://www.youtube.com/watch?v=Uc6d-qOxI0c",
    "Étirement des ischios": "https://www.youtube.com/watch?v=vA6qj6suhN4",
    "Développé épaules avec haltères": "https://www.youtube.com/watch?v=qEwKCR5JCog",
    "Rowing avec haltères": "https://www.youtube.com/watch?v=roCP6wCXPqo",
    "Respiration lente": "https://www.youtube.com/watch?v=Yjvwkde95w0",
    "Étirement doux": "https://www.youtube.com/watch?v=4bxSqGW89YM",
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
    st.caption(f"La démonstration reste dans l’app et tourne en boucle pendant tes {seconds} secondes.")
    st.video(
        EXERCISE_VIDEOS[name],
        loop=True,
        autoplay=True,
        muted=True,
        width="stretch",
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
st.caption("Un coach vidéo directement dans ton téléphone")

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

st.caption("Version 3 — vidéos intégrées et bouclées dans l’app, sans coût OpenAI.")
