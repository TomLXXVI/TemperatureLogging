from datetime import datetime
import streamlit as st
from temperature_logging import MeasurementFileReader, plot_chart


st.set_page_config(layout='wide')


@st.experimental_memo
def get_measurement_file_reader() -> MeasurementFileReader:
    mfr = MeasurementFileReader('./data')
    mfr.batch_read()
    return mfr


mfr = get_measurement_file_reader()
log_start, log_end = mfr.get_datetime_limits()

st.title('Temperatuurlogging DEMRO')

selected_dates = st.sidebar.date_input(
    label='Selecteer start- en einddatum',
    value=(log_start.date(), log_end.date()),
    min_value=log_start.date(),
    max_value=log_end.date()
)

selected_locations = st.sidebar.multiselect(
    label='Selecteer locaties',
    options=mfr.locations,
    default=mfr.locations[0]
)

if len(selected_dates) == 2:
    start = datetime.combine(selected_dates[0], datetime.min.time())
    end = datetime.combine(selected_dates[1], datetime.min.time())
    measurement_data = mfr.get_measurements(start, end, selected_locations)
    chart = plot_chart(measurement_data, 0, 2, width=1450)
    st.plotly_chart(chart)
