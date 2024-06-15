import streamlit as st
import os
import streamlit.components.v1 as components

# Ruta a la carpeta de construcción de React
build_dir = os.path.join(os.path.dirname(__file__), 'build')

def main_interface():
    # Título de la aplicación
    st.title("Training Dialer Assistant")

    # Embeber la aplicación React en Streamlit
    with open(os.path.join(build_dir, 'index.html')) as f:
        html_content = f.read()

    # Script para escuchar el evento 'endCall' y cambiar la vista en Streamlit
    script = """
    <script type="text/javascript">
      document.addEventListener('endCall', function() {
        window.parent.postMessage({ type: 'endCall' }, '*');
      });

      // Iniciar el temporizador para refrescar la página cada 10 segundos
      function initTimer(periodInSeconds) {
          var end = Date.now() + periodInSeconds * 1000;

          var x = window.setInterval(function() {
              var timeLeft = Math.floor((end - Date.now()) / 1000);

              if(timeLeft < 0) { clearInterval(x); return; }

              document.getElementById('div').innerHTML = '00:' + (timeLeft < 10 ? '0' + timeLeft : timeLeft);
          },200);
      }

      initTimer(10);
    </script>
    """

    components.html(html_content + script, height=800, scrolling=True)

def waiting_interface():
    # Título de la pantalla de espera
    st.title('Waiting for Evaluation Results')

    # Informar al usuario que el sistema está recuperando resultados
    st.write(f"Please wait, retrieving results for call ID: {st.session_state.get('call_id', 'unknown')}")

    # Botón para regresar a la pantalla principal
    if st.button("Back to Home"):
        st.session_state['current_view'] = 'main'
        st.experimental_rerun()

    # Ruta al archivo donde se almacenan los resultados de las llamadas
    filepath = "output_files/califications_history.jsonl"
    found = False
    attempts = 0

    # Consultar el archivo en busca de resultados
    while not found and attempts < 1000:
        with open(filepath, 'r') as file:
            for line in file:
                data = json.loads(line)
                if data.get("call_id") == st.session_state.get('call_id'):
                    found = True
                    st.session_state['data'] = data
                    st.session_state['current_view'] = 'results'
                    st.experimental_rerun()
                    return
        time.sleep(1)  # Retraso entre intentos
        attempts += 1

    # Si no se encuentran resultados, mostrar un mensaje de error
    if not found:
        st.error("Failed to retrieve results after several attempts. Please try again later.")

def results_interface():
    # Título de la interfaz de resultados
    st.title('Evaluation Results for Customer Interaction')

    # Botón para regresar a la pantalla principal
    if st.button("Back to Home"):
        st.session_state['current_view'] = 'main'
        st.experimental_rerun()

    # Recuperar los datos de evaluación almacenados en el estado de la sesión
    data = st.session_state.get('data', {})

    # Verificar si los datos de calificación están disponibles y analizarlos
    if 'calification' in data:
        calification_data = json.loads(data["calification"])
        st.subheader('Metrics of evaluation (0-10):')

        # Mostrar las métricas de los datos de calificación
        for key, value in calification_data.items():
            if key not in ["Notes", "call_id"]:
                st.metric(label=key, value=value)

        # Mostrar notas detalladas si están disponibles
        if "Notes" in calification_data:
            st.subheader('Detailed Notes:')
            st.write(calification_data["Notes"])
        else:
            st.write("No detailed notes available.")
    else:
        st.error("Calification data not found in the response.")

    # Mostrar los datos JSON completos para su revisión
    st.subheader('JSON Complete:')
    st.json(data)  # Mostrar los datos JSON completos

# Inicializar el estado de la aplicación
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'main'

# Gestionar la vista actual de la aplicación según el estado
query_params = st.experimental_get_query_params()
st.session_state['current_view'] = query_params.get("view", ["main"])[0]

if st.session_state['current_view'] == 'main':
    main_interface()
elif st.session_state['current_view'] == 'waiting':
    waiting_interface()
elif st.session_state['current_view'] == 'results':
    results_interface()

# Establecer el parámetro de consulta según la vista actual
st.experimental_set_query_params(view=st.session_state['current_view'])
