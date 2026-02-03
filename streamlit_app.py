import streamlit as st
import re

st.set_page_config(page_title="TT Edge Desk", layout="centered")

st.title("🏓 TT Edge Desk")
st.caption("EV + stake (Kelly fraccional). Prototipo: tú pegas cuota + prob modelo (p).")

st.divider()

bankroll = st.number_input("💰 Banca actual (COP)", min_value=0, step=1000, value=50000)
target = st.number_input("🎯 Objetivo (COP)", min_value=0, step=1000, value=80000)

st.divider()

st.subheader("📋 Pega tus picks (una por línea)")
st.caption("Formato recomendado:  Jugador A vs Jugador B @1.85 | p=0.62")
raw = st.text_area(
    "Picks",
    height=200,
    placeholder="Player A vs Player B @1.85 | p=0.62\nPlayer C vs Player D @2.05 | p=0.55"
)

st.markdown("**Parámetros de riesgo**")
kelly_fraction = st.slider("Kelly fraccional (más bajo = más seguro)", 0.05, 0.50, 0.25, 0.05)
max_stake_pct = st.slider("Tope stake por pick (% de banca)", 1, 20, 8, 1)
min_edge = st.slider("Edge mínimo para considerar (p - p_implícita)", 0.00, 0.20, 0.03, 0.01)

st.divider()

def parse_line(line: str):
    """
    Espera: "A vs B @1.85 | p=0.62"
    - match: texto antes de @
    - odds: número después de @
    - p: número después de p=
    """
    # odds
    m_odds = re.search(r"@(\s*\d+(\.\d+)?)", line)
    # p
    m_p = re.search(r"p\s*=\s*(0(\.\d+)?|1(\.0+)?)", line)

    if not m_odds or not m_p:
        return None

    odds = float(m_odds.group(1).strip())
    p = float(m_p.group(0).split("=")[1].strip())

    match_part = line.split("@")[0].strip()
    if not match_part:
        match_part = line.strip()

    return match_part, odds, p

def implied_prob(odds: float) -> float:
    return 1.0 / odds if odds > 0 else 0.0

def edge(p: float, odds: float) -> float:
    return p - implied_prob(odds)

def ev(p: float, odds: float) -> float:
    # retorno esperado por 1 unidad apostada: p*odds - 1
    return (p * odds) - 1.0

def kelly_stake_fraction(p: float, odds: float) -> float:
    """
    Kelly para decimal odds:
    b = odds - 1
    f* = (b*p - (1-p)) / b = (p*odds - 1) / (odds - 1)
    """
    b = odds - 1.0
    if b <= 0:
        return 0.0
    f = (p * odds - 1.0) / b
    return max(0.0, f)

def stake_cop(bankroll: float, p: float, odds: float) -> int:
    f = kelly_stake_fraction(p, odds)
    f = f * kelly_fraction
    f = min(f, max_stake_pct / 100.0)
    return int(round(bankroll * f / 1000.0) * 1000)  # redondeo a miles COP

if st.button("🔍 Analizar"):
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    parsed = []
    bad_lines = []

    for line in lines:
        item = parse_line(line)
        if item is None:
            bad_lines.append(line)
        else:
            match, odds, p = item
            ip = implied_prob(odds)
            e = p - ip
            expv = ev(p, odds)
            stake = stake_cop(bankroll, p, odds)
            parsed.append({
                "Match": match,
                "Cuota": odds,
                "p_modelo": p,
                "p_implícita": ip,
                "Edge": e,
                "EV": expv,
                "Stake(COP)": stake,
                "Apuesta?": "SÍ" if (e >= min_edge and expv > 0) else "NO"
            })

    if not parsed:
        st.error("No pude leer nada. Asegúrate de usar el formato:  A vs B @1.85 | p=0.62")
        if bad_lines:
            st.write("Líneas inválidas:")
            for b in bad_lines[:8]:
                st.code(b)
        st.stop()

    # ordenar por edge desc
    parsed_sorted = sorted(parsed, key=lambda x: (x["Apuesta?"] == "SÍ", x["Edge"]), reverse=True)

    st.success("Listo. Tabla EV + Edge + stake:")
    st.dataframe(parsed_sorted, use_container_width=True)

    st.divider()
    st.subheader("🎯 Portafolios sugeridos (solo picks con 'SÍ')")

    yes = [x for x in parsed_sorted if x["Apuesta?"] == "SÍ"]
    if not yes:
        st.warning("Hoy no hay apuestas con edge mínimo. Eso también es ganar: NO apostar.")
    else:
        A = yes[:1]
        B = yes[:2]
        C = yes[:3]

        def render_portfolio(name, items):
            st.markdown(f"### {name}")
            total_stake = sum(i["Stake(COP)"] for i in items)
            st.write(f"Total stake: **{total_stake:,} COP**")
            for i in items:
                st.write(f"- **{i['Match']}** @ **{i['Cuota']}** | p={i['p_modelo']:.2f} | edge={i['Edge']:.3f} | stake={i['Stake(COP)']:,}")

        render_portfolio("🅰️ A (Conservador)", A)
        render_portfolio("🅱️ B (Balanceado)", B)
        render_portfolio("🅾️ C (Agresivo)", C)

st.divider()

st.subheader("📊 Actualizar resultado (manual)")
res = st.radio("¿Cómo te fue?", ["Ganaste", "Perdiste"])
new_bankroll = st.number_input("💼 Nueva banca (COP)", min_value=0, step=1000, value=bankroll)

if st.button("💾 Guardar resultado"):
    st.success(f"Guardado ✅ Resultado: {res} | Banca: {new_bankroll:,} COP")
    st.info("Siguiente upgrade: guardar historial en un archivo (CSV) dentro del repo.")
