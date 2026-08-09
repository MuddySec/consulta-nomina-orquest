import json
from datetime import date

import streamlit as st

from orquest_payroll import get_enriched_payroll, get_restaurants


st.set_page_config(
    page_title="Consulta Nómina Orquest",
    page_icon="📊",
    layout="centered",
)

st.title("Consulta Nómina Orquest")
st.write("Selecciona restaurante y fechas para obtener el JSON de nómina.")


@st.cache_data(ttl=3600)
def load_restaurants_cached():
    return get_restaurants()


try:
    restaurants = load_restaurants_cached()
except Exception as e:
    st.error(f"No se pudieron cargar los restaurantes: {e}")
    st.stop()


if not restaurants:
    st.error("No se ha recibido ningún restaurante desde Orquest.")
    st.stop()


with st.form("consulta_nomina"):
    selected_restaurant = st.selectbox(
        "Restaurante",
        options=restaurants,
        format_func=lambda r: r["label"],
    )

    col1, col2 = st.columns(2)

    with col1:
        from_date = st.date_input(
            "Fecha inicio",
            value=date.today(),
        )

    with col2:
        to_date = st.date_input(
            "Fecha fin",
            value=date.today(),
        )

    submitted = st.form_submit_button("Consultar nómina")


if submitted:
    service_id = selected_restaurant["id"]
    restaurant_name = selected_restaurant["name"]

    if from_date > to_date:
        st.error("La fecha de inicio no puede ser posterior a la fecha fin.")

    else:
        from_str = from_date.isoformat()
        to_str = to_date.isoformat()

        try:
            with st.spinner("Consultando Orquest..."):
                data = get_enriched_payroll(service_id, from_str, to_str)

            st.success("Consulta realizada correctamente.")

            st.write(f"Restaurante: **{restaurant_name}**")
            st.write(f"ID Orquest: `{service_id}`")

            if isinstance(data, list):
                st.write(f"Registros recibidos: **{len(data)}**")
            else:
                st.write("Respuesta recibida de Orquest.")

            json_text = json.dumps(data, indent=2, ensure_ascii=False)

            st.info("El JSON ya está listo. Puedes descargarlo aquí:")

            st.download_button(
                label="⬇️ Descargar JSON de nómina",
                data=json_text,
                file_name=f"nomina_{service_id}_{from_str}_{to_str}.json",
                mime="application/json",
                type="primary",
                use_container_width=True,
            )

            st.subheader("JSON recibido")
            st.json(data)

        except Exception as e:
            st.error(f"Error al consultar Orquest: {e}")