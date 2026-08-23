import hmac
import json

import requests
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Fitness Coach", page_icon="💪", layout="centered")

GIF_BASE = "https://raw.githubusercontent.com/mohamedatef90/exercise-library/main/gifs/"
MUSIC_URL = "https://upload.wikimedia.org/wikipedia/commons/0/09/Guillaume_Tell_-_Overture_-_%28Rossini%2C_Gioacchino%29_by_Fritz_Reiner_%28conductor%29.mp3"


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


# Uniquement des mouvements dont le média existe réellement dans le dépôt GitHub.
# Format : nom affiché, fichier GIF, consigne, durée de base.
EXERCISES = {
    "Échauffement": [
        ("Cercles de chevilles", "uL9CsKm.gif", "Fais des rotations lentes dans les deux sens.", 30),
        ("Étirement quadriceps à quatre pattes", "qBcKorM.gif", "Bouge lentement et reste dans une amplitude confortable.", 35),
    ],
    "Renforcement": [
        ("Pompes profondes", "vptOQ4N.gif", "Corps gainé, descends sous contrôle puis pousse sans creuser le dos.", 35),
        ("Pont fessier", "u0cNiij.gif", "Pousse dans les talons et serre les fessiers en haut.", 40),
        ("Abdos 3/4 sit-up", "2gPfomN.gif", "Monte le buste sous contrôle sans tirer sur la nuque.", 35),
        ("Toucher de talons alterné", "qaZVsGk.gif", "Garde les abdos engagés et alterne droite et gauche.", 35),
    ],
    "Cardio": [
        ("Mountain climbers", "RJgzwny.gif", "Garde le bassin stable et alterne les genoux à un rythme régulier.", 35),
        ("Burpees", "dK9394r.gif", "Reste contrôlé ; enlève le saut si nécessaire.", 30),
        ("Fentes marchées genoux hauts", "J9zIWig.gif", "Reste droit et avance avec contrôle.", 40),
    ],
    "Haltères": [
        ("Élévations latérales haltères", "DsgkuIt.gif", "Épaules basses, monte les bras sans élan.", 35),
    ],
}


@st.cache_data(ttl=86400, show_spinner=False, max_entries=20)
def load_gif(filename: str):
    try:
        response = requests.get(GIF_BASE + filename, timeout=30)
        response.raise_for_status()
        if len(response.content) < 1024:
            return None
        return response.content
    except requests.RequestException:
        return None


def background_music_player():
    """Lecteur de fond : morceau connu, librement réutilisable, volume bas."""
    components.html(
        f"""
        <div style="font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif; color:#ddd;">
          <audio id="fitnessMusic" controls loop preload="metadata" style="width:100%; height:40px;">
            <source src="{MUSIC_URL}" type="audio/mpeg">
          </audio>
          <div style="font-size:11px; color:#8d8d8d; margin-top:5px; line-height:1.25;">
            Rossini — <i>Ouverture de Guillaume Tell</i>, interprétation Fritz Reiner / Chicago Symphony Orchestra.
            Source : Wikimedia Commons, CC BY-SA 4.0.
          </div>
        </div>
        <script>
          const music = document.getElementById('fitnessMusic');
          music.volume = 0.18;
        </script>
        """,
        height=76,
    )


def voice_coach(name: str, instruction: str, seconds: int):
    """Utilise la synthèse vocale du navigateur/iPhone, sans API externe."""
    text = f"{name}. {instruction} Fais ce mouvement pendant {seconds} secondes."
    safe_text = json.dumps(text, ensure_ascii=False)

    components.html(
        f"""
        <div style="font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;">
          <button onclick="speakCoach()" style="
            width:100%; border:0; border-radius:12px; padding:11px 14px;
            font-size:16px; font-weight:600; cursor:pointer;
            background:#262730; color:white;">
            🔊 Réécouter l’explication
          </button>
        </div>
        <script>
          const coachText = {safe_text};
          let alreadySpoken = false;

          function speakCoach() {{
            if (!('speechSynthesis' in window)) return;
            window.speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance(coachText);
            u.lang = 'fr-FR';
            u.rate = 0.92;
            u.pitch = 1.0;
            u.volume = 1.0;
            const voices = window.speechSynthesis.getVoices();
            const french = voices.find(v => (v.lang || '').toLowerCase().startsWith('fr'));
            if (french) u.voice = french;
            window.speechSynthesis.speak(u);
            alreadySpoken = true;
          }}

          function autoSpeak() {{
            if (!alreadySpoken) speakCoach();
          }}

          if (window.speechSynthesis.getVoices().length > 0) {{
            setTimeout(autoSpeak, 550);
          }} else {{
            window.speechSynthesis.onvoiceschanged = () => setTimeout(autoSpeak, 300);
            setTimeout(autoSpeak, 1200);
          }}
        </script>
        """,
        height=54,
    )


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
        pool = EXERCISES["Échauffement"] + EXERCISES["Renforcement"][1:2]
    else:
        pool = EXERCISES["Renforcement"][:3] + EXERCISES["Cardio"][:2]

    if equipment == "Haltères légers":
        pool += EXERCISES["Haltères"]

    rounds = 1 if duration <= 15 else 2 if duration <= 30 else 3
    if level == "Débutant":
        rounds = max(1, rounds - 1)
    elif level == "Avancé":
        rounds += 1

    for _ in range(rounds):
        session.extend(pool)

    return [
        (name, gif_file, instruction, adjusted_seconds(seconds, level))
        for name, gif_file, instruction, seconds in session
    ]


def next_readable(workout, start_index: int):
    for candidate_idx in range(start_index, len(workout)):
        gif_bytes = load_gif(workout[candidate_idx][1])
        if gif_bytes:
            return candidate_idx, gif_bytes
    return None, None


st.title("💪 Fitness Coach")
st.caption("Démonstrations animées + musique + coach vocal français")

if not check_password():
    st.stop()

with st.expander("⚠️ Sécurité", expanded=False):
    st.write(
        "Fais les mouvements dans une amplitude confortable. Arrête-toi en cas de douleur, malaise, "
        "essoufflement inhabituel ou vertiges. Cette app ne remplace pas un avis médical ou un coach qualifié."
    )

st.subheader("🎵 Musique")
st.caption("Rossini — Ouverture de Guillaume Tell. Appuie sur ▶️ pour démarrer ; le volume est volontairement bas pour entendre le coach.")
background_music_player()

st.subheader("🔊 Coach")
voice_enabled = st.toggle("Coach vocal automatique", value=True)

st.subheader("Créer ma séance")
goal = st.selectbox(
    "Objectif",
    ["Forme générale", "Se muscler", "Cardio / brûler des calories", "Mobilité / récupération"],
)
level = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé"])
duration = st.select_slider("Durée", options=[10, 15, 20, 30, 45], value=20, format_func=lambda x: f"{x} min")
equipment = st.selectbox("Matériel", ["Aucun", "Haltères légers"])

if st.button("Créer la séance", type="primary", use_container_width=True):
    workout = build_session(goal, duration, level, equipment)
    with st.spinner("Préparation de la première démonstration…"):
        first_idx, first_gif = next_readable(workout, 0)

    if first_idx is not None:
        st.session_state["workout"] = workout
        st.session_state["exercise_index"] = first_idx
        st.session_state["current_gif"] = first_gif
        st.session_state["workout_meta"] = {
            "goal": goal,
            "duration": duration,
            "level": level,
            "equipment": equipment,
        }
    else:
        st.error("Les démonstrations ne sont pas accessibles pour le moment.")

workout = st.session_state.get("workout")

if workout:
    idx = min(st.session_state.get("exercise_index", 0), len(workout) - 1)
    name, gif_file, instruction, seconds = workout[idx]
    meta = st.session_state.get("workout_meta", {})

    gif_bytes = st.session_state.get("current_gif") or load_gif(gif_file)
    if not gif_bytes:
        next_idx, next_gif = next_readable(workout, idx + 1)
        if next_idx is not None:
            st.session_state["exercise_index"] = next_idx
            st.session_state["current_gif"] = next_gif
            st.rerun()
        st.error("Aucune autre démonstration disponible dans cette séance.")
        st.stop()

    st.divider()
    st.caption(
        f"{meta.get('goal', '')} • {meta.get('duration', '')} min • {meta.get('level', '')} • {meta.get('equipment', '')}"
    )
    st.progress((idx + 1) / len(workout))
    st.write(f"Exercice {idx + 1} sur {len(workout)}")
    st.header(name)
    st.metric("Durée", f"{seconds} sec")
    st.info(instruction)

    if voice_enabled:
        voice_coach(name, instruction, seconds)

    st.subheader("🎥 Suis le coach")
    st.image(gif_bytes, width="stretch")
    st.caption("Animation chargée directement depuis GitHub : pas de serveur vidéo externe.")

    st.write(f"⏱️ Fais le mouvement pendant **{seconds} secondes**, puis passe au suivant.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Précédent", use_container_width=True, disabled=idx == 0):
            previous_idx = idx - 1
            while previous_idx >= 0:
                previous_gif = load_gif(workout[previous_idx][1])
                if previous_gif:
                    st.session_state["exercise_index"] = previous_idx
                    st.session_state["current_gif"] = previous_gif
                    st.rerun()
                previous_idx -= 1

    with col2:
        if idx < len(workout) - 1:
            if st.button("Suivant ➡️", type="primary", use_container_width=True):
                next_idx, next_gif = next_readable(workout, idx + 1)
                if next_idx is not None:
                    st.session_state["exercise_index"] = next_idx
                    st.session_state["current_gif"] = next_gif
                    st.rerun()
                st.success("Séance terminée.")
        else:
            if st.button("✅ Terminer", type="primary", use_container_width=True):
                st.success("Séance terminée. Bravo !")
                st.balloons()

    if st.button("🔄 Recommencer cette séance", use_container_width=True):
        first_idx, first_gif = next_readable(workout, 0)
        if first_idx is not None:
            st.session_state["exercise_index"] = first_idx
            st.session_state["current_gif"] = first_gif
            st.rerun()

st.caption("Version test — médias stables sur GitHub, Rossini en fond et voix française du navigateur.")
