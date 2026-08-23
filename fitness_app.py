import hmac

import requests
import streamlit as st


st.set_page_config(page_title="Fitness Coach HD", page_icon="💪", layout="centered")

API_URL = "https://exercise-database.zenithfits.com/api/v1/exercises?limit=317"


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


# On utilise uniquement des exercices présents dans le catalogue HD de test.
# Le nom anglais sert à retrouver automatiquement la vidéo ; le reste est affiché en français.
EXERCISES = {
    "Échauffement": [
        ("Échauffement épaules", "Band Shoulder Warm-Up Stretch", "Mobilise les épaules sans forcer.", 35),
        ("Cercles des poignets", "Wrist Circles", "Fais des rotations lentes dans les deux sens.", 30),
        ("Mobilité chevilles", "Feet and Ankles Rotation Stretch", "Tourne les chevilles doucement et garde l’équilibre.", 30),
    ],
    "Renforcement": [
        ("Squats", "Squat", "Poitrine haute, genoux dans l’axe des pieds, pousse les hanches vers l’arrière.", 40),
        ("Pompes", "Deep Push-Up", "Corps gainé, descends sous contrôle et pousse sans creuser le dos.", 35),
        ("Pont fessier", "Bridge Pose (Setu Bandhasana)", "Pousse dans les talons et serre les fessiers en haut.", 40),
        ("Étirement en position quadrupède", "All Fours Groin Stretch", "Bouge lentement et reste dans une amplitude confortable.", 40),
    ],
    "Cardio": [
        ("Jumping jacks", "Jumping Jack", "Garde un rythme régulier et atterris souplement.", 40),
        ("Burpees", "Burpee", "Reste contrôlé ; ralentis ou enlève le saut si nécessaire.", 30),
        ("Course sur place", "Running", "Buste droit, bras actifs, cadence confortable.", 45),
    ],
    "Mobilité": [
        ("Étirement fléchisseurs de hanche", "Standing Hip Flexor and Abdominal Stretch", "Bassin légèrement rentré, ne cambre pas le bas du dos.", 40),
        ("Étirement ischios", "Single Straight Leg Stretch", "Garde le mouvement lent et évite les à-coups.", 40),
        ("Rotation du buste", "Chest Lift with Rotation", "Tourne depuis le haut du dos sans forcer la nuque.", 40),
        ("Étirement adducteurs", "All Fours Groin Stretch", "Respire calmement et garde une amplitude confortable.", 40),
    ],
    "Haltères": [
        ("Développé épaules haltères", "Dumbbell Alternating Shoulder Press", "Abdos serrés, pousse au-dessus de la tête sans cambrer.", 35),
        ("Rowing haltères", "Dumbbell Bent-Over Row", "Dos long, tire les coudes vers l’arrière sans hausser les épaules.", 40),
    ],
}


@st.cache_data(ttl=86400, show_spinner=False)
def load_catalogue():
    response = requests.get(API_URL, timeout=20)
    response.raise_for_status()
    payload = response.json()
    data = payload.get("data", [])
    return data if isinstance(data, list) else []


def normalize(text: str) -> str:
    return " ".join(text.lower().replace("-", " ").split())


def find_exercise(catalogue, api_name: str):
    target = normalize(api_name)

    # Exact match first.
    for item in catalogue:
        if normalize(item.get("name", "")) == target:
            return item

    # Then aliases.
    for item in catalogue:
        aliases = item.get("aliases", []) or []
        for alias in aliases:
            if normalize(str(alias)) == target:
                return item

    # Last resort: contained-name match.
    for item in catalogue:
        candidate = normalize(item.get("name", ""))
        if target in candidate or candidate in target:
            return item

    return None


def female_video(item):
    if not item:
        return None
    videos = item.get("videos", {}) or {}
    return videos.get("female") or videos.get("male")


def adjusted_seconds(seconds: int, level: str) -> int:
    if level == "Débutant":
        return max(20, seconds - 5)
    if level == "Avancé":
        return seconds + 10
    return seconds


def build_session(goal: str, duration: int, level: str, equipment: str):
    session = list(EXERCISES["Échauffement"])

    if goal == "Se muscler":
        pool = EXERCISES["Renforcement"]
    elif goal == "Cardio / brûler des calories":
        pool = EXERCISES["Cardio"] + EXERCISES["Renforcement"][:2]
    elif goal == "Mobilité / récupération":
        pool = EXERCISES["Mobilité"]
    else:
        pool = EXERCISES["Renforcement"][:3] + EXERCISES["Cardio"][:2]

    if equipment == "Haltères légers":
        pool = pool + EXERCISES["Haltères"]

    rounds = 1 if duration <= 15 else 2 if duration <= 30 else 3
    if level == "Débutant":
        rounds = max(1, rounds - 1)
    elif level == "Avancé":
        rounds += 1

    for _ in range(rounds):
        session.extend(pool)

    return [
        (label, api_name, instruction, adjusted_seconds(seconds, level))
        for label, api_name, instruction, seconds in session
    ]


st.title("💪 Fitness Coach HD")
st.caption("Prototype avec vraies démonstrations vidéo Full‑HD directement dans l’app")

if not check_password():
    st.stop()

with st.expander("⚠️ Sécurité", expanded=False):
    st.write(
        "Fais les mouvements dans une amplitude confortable. Arrête-toi en cas de douleur, malaise, "
        "essoufflement inhabituel ou vertiges. Cette app ne remplace pas un avis médical ou un coach qualifié."
    )

try:
    with st.spinner("Chargement du catalogue vidéo HD…"):
        catalogue = load_catalogue()
except Exception as exc:
    catalogue = []
    st.error(f"Le catalogue HD n’a pas pu être chargé pour le moment : {exc}")

if catalogue:
    st.success(f"Catalogue HD chargé : {len(catalogue)} exercices")

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
    label, api_name, instruction, seconds = workout[idx]
    meta = st.session_state.get("workout_meta", {})

    st.divider()
    st.caption(
        f"{meta.get('goal', '')} • {meta.get('duration', '')} min • {meta.get('level', '')} • {meta.get('equipment', '')}"
    )
    st.progress((idx + 1) / len(workout))
    st.write(f"Exercice {idx + 1} sur {len(workout)}")
    st.header(label)
    st.metric("Durée", f"{seconds} sec")
    st.info(instruction)

    item = find_exercise(catalogue, api_name) if catalogue else None
    video_url = female_video(item)

    st.subheader("🎥 Suis le coach")
    if video_url:
        st.video(video_url, autoplay=True, loop=True, muted=True, width="stretch")
        st.caption("Mode prototype HD : version féminine utilisée en priorité pour garder le rendu le plus cohérent possible.")
    else:
        st.warning("Vidéo HD non trouvée pour ce mouvement dans le catalogue de test.")

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

st.caption(
    "Version HD prototype — vidéos chargées à distance pour évaluation. "
    "Avant une diffusion publique/commerciale, nous choisirons une bibliothèque avec licence et provenance vidéo clairement garanties."
)
