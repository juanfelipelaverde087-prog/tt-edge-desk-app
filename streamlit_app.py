import streamlit as st

st.set_page_config(page_title="TT Edge Desk", layout="centered")

st.title("🏓 TT Edge Desk")
st.caption("Prototipo simple: cuotas → recomendación A/B/C + gestión de banca")

st.divider()

bankroll = st.number_input("💰 Banca actual (COP)", min_value=0, step=1000, value=50000)
target = st.number_input("🎯 Objetivo (COP)", min_value=0, step=1000, value=80000)

st.divider()

st.subheader("📋 Pega tus cuotas (una por línea)")
st.caption("Formato: Jugador A vs Jugador B @1.85")
raw = st.text_area("Cuotas", height=160, placeholder="Player A vs Player B @1.85\nPlayer C vs Player D @2.05")

def parse_lines(text: str):
    rows = []
    for line in [l.strip() for l in text.splitlines() if l.strip()]:
        try:
            left, odds_str = [x.strip() for x in line.split("@")]
            a, b = [x.strip() for x in left.split("vs")]
            odds = float(odds_str)
            rows.append((a, b, odds))
        except:
            rows.append(("ERROR", line, 0.0))
    return rows

if st.button("🔍 Analizar"):
    rows = parse_lines(raw)
    bad = [r for r in rows if r[0] == "ERROR"]
    if not rows or len(rows) == len(bad):
        st.error("Pega cuotas válidas (ej: A vs B @1.85)")
    else:
        st.success("Listo. Aquí van tus opciones (prototipo).")

        ok = [r for r in rows if r[0] != "ERROR"]
        ok_sorted = sorted(ok, key=lambda x: x[2])

        A = ok_sorted[:1]
        B = ok_sorted[:2]
        C = ok_sorted[:3]

        st.markdown("### 🅰️ Opción A (Conservadora)")
        st.write("Stake sugerido:", int(max(2000, bankroll * 0.10)))
        for a,b,odds in A:
            st.write(f"- **{a}** vs {b} @ **{odds}**")

        st.markdown("### 🅱️ Opción B (Balanceada)")
        st.write("Stake por pick sugerido:", int(max(2000, bankroll * 0.08)))
        for a,b,odds in B:
            st.write(f"- **{a}** vs {b} @ **{odds}**")

        st.markdown("### 🅾️ Opción C (Agresiva)")
        st.write("Stake por pick sugerido:", int(max(2000, bankroll * 0.06)))
        for a,b,odds in C:
            st.write(f"- **{a}** vs {b} @ **{odds}**")

        st.info("Prototipo inicial. Luego metemos datos reales + EV.")

st.divider()

st.subheader("📊 Actualizar resultado")
res = st.radio("¿Cómo te fue?", ["Ganaste", "Perdiste"])
new_bankroll = st.number_input("💼 Nueva banca (COP)", min_value=0, step=1000, value=bankroll)

if st.button("💾 Guardar"):
    st.success(f"Guardado ✅ Resultado: {res} | Banca: {new_bankroll:,} COP")
