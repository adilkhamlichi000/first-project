import hmac
import json

import requests
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Fitness Coach", page_icon="💪", layout="centered")

GIF_BASE = "https://raw.githubusercontent.com/mohamedatef90/exercise-library/main/gifs/"
# Hype Energy — The_Mountain, Pixabay Content License.
MUSIC_URL = "https://pixabay.com/music/download/id-171614.mp3"
EXERCISE_SECONDS = 30


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

    # Tous les mouvements durent exactement 30 secondes.
    return [
        (name, gif_file, instruction, EXERCISE_SECONDS)
        for name, gif_file, instruction, _ in session
    ]


def next_readable(workout, start_index: int):
    for candidate_idx in range(start_index, len(workout)):
        gif_bytes = load_gif(workout[candidate_idx][1])
        if gif_bytes:
            return candidate_idx, gif_bytes
    return None, None


def coach_text(exercise):
    name, _, instruction, seconds = exercise
    return f"{name}. {instruction} Fais ce mouvement pendant {seconds} secondes."


def install_start_audio(first_exercise):
    text = json.dumps(coach_text(first_exercise), ensure_ascii=False)
    music_url = json.dumps(MUSIC_URL)

    components.html(
        f"""
        <script>
        (() => {{
          const P = window.parent;
          const D = P.document;

          function isMuted() {{
            return localStorage.getItem('fitnessMuted') === '1';
          }}

          function getMusic() {{
            let audio = D.getElementById('fitnessGlobalMusic');
            if (!audio) {{
              audio = D.createElement('audio');
              audio.id = 'fitnessGlobalMusic';
              audio.src = {music_url};
              audio.loop = true;
              audio.preload = 'auto';
              audio.playsInline = true;
              audio.style.display = 'none';
              D.body.appendChild(audio);
            }}
            audio.volume = 0.16;
            return audio;
          }}

          function speak(text) {{
            if (isMuted()) return;
            try {{
              const synth = P.speechSynthesis;
              if (!synth || !P.SpeechSynthesisUtterance) return;
              synth.cancel();
              const u = new P.SpeechSynthesisUtterance(text);
              u.lang = 'fr-FR';
              u.rate = 0.92;
              u.pitch = 1.0;
              u.volume = 1.0;
              const voices = synth.getVoices();
              const fr = voices.find(v => (v.lang || '').toLowerCase().startsWith('fr'));
              if (fr) u.voice = fr;
              const music = getMusic();
              u.onstart = () => {{ music.volume = 0.045; }};
              u.onend = () => {{ if (!isMuted()) music.volume = 0.16; }};
              u.onerror = () => {{ if (!isMuted()) music.volume = 0.16; }};
              synth.speak(u);
            }} catch (e) {{}}
          }}

          if (P.__fitnessStartHandler) D.removeEventListener('click', P.__fitnessStartHandler, true);

          P.__fitnessStartHandler = (event) => {{
            const button = event.target.closest ? event.target.closest('button') : null;
            if (!button) return;
            const label = (button.innerText || button.textContent || '').trim();
            if (!label.includes('Créer la séance')) return;

            localStorage.setItem('fitnessMuted', '0');
            const music = getMusic();
            music.currentTime = 0;
            music.volume = 0.16;
            music.play().catch(() => {{}});
            P.__fitnessSessionActive = true;
            speak({text});
          }};

          D.addEventListener('click', P.__fitnessStartHandler, true);
        }})();
        </script>
        """,
        height=0,
    )


def install_navigation_audio(workout, idx):
    current = coach_text(workout[idx])
    next_text = coach_text(workout[idx + 1]) if idx + 1 < len(workout) else "Séance terminée. Bravo."
    previous_text = coach_text(workout[idx - 1]) if idx > 0 else current
    first_text = coach_text(workout[0])

    safe = json.dumps(
        {"current": current, "next": next_text, "previous": previous_text, "first": first_text},
        ensure_ascii=False,
    )
    music_url = json.dumps(MUSIC_URL)

    components.html(
        f"""
        <script>
        (() => {{
          const P = window.parent;
          const D = P.document;
          const texts = {safe};

          function isMuted() {{
            return localStorage.getItem('fitnessMuted') === '1';
          }}

          function getMusic() {{
            let audio = D.getElementById('fitnessGlobalMusic');
            if (!audio) {{
              audio = D.createElement('audio');
              audio.id = 'fitnessGlobalMusic';
              audio.src = {music_url};
              audio.loop = true;
              audio.preload = 'auto';
              audio.playsInline = true;
              audio.style.display = 'none';
              D.body.appendChild(audio);
            }}
            return audio;
          }}

          function speak(text) {{
            if (isMuted()) return;
            try {{
              const synth = P.speechSynthesis;
              if (!synth || !P.SpeechSynthesisUtterance) return;
              synth.cancel();
              const u = new P.SpeechSynthesisUtterance(text);
              u.lang = 'fr-FR';
              u.rate = 0.92;
              u.pitch = 1.0;
              u.volume = 1.0;
              const voices = synth.getVoices();
              const fr = voices.find(v => (v.lang || '').toLowerCase().startsWith('fr'));
              if (fr) u.voice = fr;
              const music = getMusic();
              u.onstart = () => {{ music.volume = 0.045; }};
              u.onend = () => {{ if (!isMuted()) music.volume = 0.16; }};
              u.onerror = () => {{ if (!isMuted()) music.volume = 0.16; }};
              synth.speak(u);
            }} catch (e) {{}}
          }}

          const music = getMusic();
          if (P.__fitnessSessionActive && !isMuted()) {{
            music.volume = 0.16;
            music.play().catch(() => {{}});
          }}

          if (P.__fitnessNavHandler) D.removeEventListener('click', P.__fitnessNavHandler, true);
          if (P.__fitnessSoundHandler) D.removeEventListener('click', P.__fitnessSoundHandler, true);

          P.__fitnessNavHandler = (event) => {{
            const button = event.target.closest ? event.target.closest('button') : null;
            if (!button) return;
            const label = (button.innerText || button.textContent || '').trim();

            if (label.includes('Suivant')) speak(texts.next);
            else if (label.includes('Précédent')) speak(texts.previous);
            else if (label.includes('Recommencer')) speak(texts.first);
          }};

          P.__fitnessSoundHandler = (event) => {{
            const button = event.target.closest ? event.target.closest('button') : null;
            if (!button) return;
            const label = (button.innerText || button.textContent || '').trim();
            const music = getMusic();

            if (label.includes('Couper le son')) {{
              localStorage.setItem('fitnessMuted', '1');
              music.pause();
              try {{ P.speechSynthesis.cancel(); }} catch (e) {{}}
            }} else if (label.includes('Remettre le son')) {{
              localStorage.setItem('fitnessMuted', '0');
              music.volume = 0.16;
              music.play().catch(() => {{}});
            }}
          }};

          D.addEventListener('click', P.__fitnessNavHandler, true);
          D.addEventListener('click', P.__fitnessSoundHandler, true);
        }})();
        </script>
        """,
        height=0,
    )


def install_auto_advance(idx: int, total: int):
    """Compte 30 secondes puis déclenche automatiquement Suivant/Terminer."""
    target_label = "Suivant" if idx < total - 1 else "Terminer"
    timer_key = json.dumps(f"{idx}-{total}")
    target = json.dumps(target_label)

    components.html(
        f"""
        <div id="fitnessCountdown" style="
          text-align:center; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;
          font-size:20px; font-weight:700; padding:5px 0 2px 0;">
          ⏱️ 30 s
        </div>
        <script>
        (() => {{
          const P = window.parent;
          const D = P.document;
          const timerKey = {timer_key};
          const targetLabel = {target};
          const countdown = document.getElementById('fitnessCountdown');

          if (P.__fitnessAutoTimer) clearTimeout(P.__fitnessAutoTimer);
          if (P.__fitnessCountdownTimer) clearInterval(P.__fitnessCountdownTimer);

          P.__fitnessTimerKey = timerKey;
          const startedAt = Date.now();

          function remaining() {{
            return Math.max(0, 30 - Math.floor((Date.now() - startedAt) / 1000));
          }}

          function renderCountdown() {{
            const left = remaining();
            if (countdown) countdown.textContent = `⏱️ ${{left}} s`;
          }}

          renderCountdown();
          P.__fitnessCountdownTimer = setInterval(renderCountdown, 250);

          P.__fitnessAutoTimer = setTimeout(() => {{
            clearInterval(P.__fitnessCountdownTimer);
            if (countdown) countdown.textContent = '⏱️ 0 s';

            const buttons = Array.from(D.querySelectorAll('button'));
            const targetButton = buttons.find(btn =>
              ((btn.innerText || btn.textContent || '').trim()).includes(targetLabel)
            );

            if (targetButton) targetButton.click();
          }}, 30000);
        }})();
        </script>
        """,
        height=48,
    )


st.title("💪 Fitness Coach")
st.caption("Démonstrations animées + Hype Energy + coach vocal français")

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

preview_workout = build_session(goal, duration, level, equipment)
install_start_audio(preview_workout[0])

if st.button("Créer la séance", type="primary", use_container_width=True):
    workout = preview_workout
    with st.spinner("Préparation de la première démonstration…"):
        first_idx, first_gif = next_readable(workout, 0)

    if first_idx is not None:
        st.session_state["workout"] = workout
        st.session_state["exercise_index"] = first_idx
        st.session_state["current_gif"] = first_gif
        st.session_state["sound_enabled"] = True
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

    install_navigation_audio(workout, idx)

    sound_enabled = st.session_state.get("sound_enabled", True)
    sound_label = "🔇 Couper le son" if sound_enabled else "🔊 Remettre le son"
    if st.button(sound_label, use_container_width=True):
        st.session_state["sound_enabled"] = not sound_enabled
        st.rerun()

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
    st.image(gif_bytes, width="stretch")

    install_auto_advance(idx, len(workout))
    st.write("Le mouvement suivant démarre automatiquement à la fin du compte à rebours.")

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

st.caption("Musique : Hype Energy — The_Mountain, Pixabay Content License.")
