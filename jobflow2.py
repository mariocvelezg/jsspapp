import os
from flask import Flask, request, render_template, send_from_directory, abort
from werkzeug.utils import secure_filename
import reglas

# --- Config ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
UPLOAD_FOLDER = STATIC_DIR  # you were already using 'static' for uploads

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Globals (initialize to avoid NameError between requests) ---
archivo_t = ''
archivo_r = ''

# --- Helpers ---
def read_matrix_any_delim(path, cast=float, minus_one=False):
    """Read space/comma/tab separated matrices robustly."""
    with open(path, 'r', encoding='utf-8') as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    for splitter in ('\t', ',', None):  # None => split on any whitespace
        try:
            rows = []
            for ln in lines:
                parts = ln.split(splitter) if splitter is not None else ln.split()
                vals = [cast(x) - 1 if minus_one else cast(x) for x in parts]
                rows.append(vals)
            return rows
        except Exception:
            # try next splitter
            continue
    raise ValueError(f"Could not parse matrix file: {path}")

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global archivo_t, archivo_r

    if request.method == 'POST':
        tiempos = request.files.get("archivo_tiempos")
        rutas = request.files.get("archivo_rutas")

        if tiempos and tiempos.filename:
            archivo_t = secure_filename(tiempos.filename)
            tiempos.save(os.path.join(app.config['UPLOAD_FOLDER'], archivo_t))

        if rutas and rutas.filename:
            archivo_r = secure_filename(rutas.filename)
            rutas.save(os.path.join(app.config['UPLOAD_FOLDER'], archivo_r))

    elif request.method == 'GET':
        archivo_t, archivo_r = '', ''

    return render_template("index.html", archivo_t=archivo_t, archivo_r=archivo_r)

@app.route('/solucion', methods=['GET', 'POST'])
def muestra_Sol():
    global archivo_t, archivo_r

    if request.method == 'GET':
        # If someone opens /solucion directly, just show the form again.
        return render_template("index.html", archivo_t=archivo_t, archivo_r=archivo_r)

    # POST:
    regla = request.form.get('regla', '').strip().lower()

    if not (archivo_t and archivo_r):
        archivo_t, archivo_r = '', ''
        return render_template("index.html", archivo_t=archivo_t, archivo_r=archivo_r)

    # --- Read inputs robustly ---
    tp_path = os.path.join(UPLOAD_FOLDER, archivo_t)
    rp_path = os.path.join(UPLOAD_FOLDER, archivo_r)

    if not os.path.exists(tp_path) or not os.path.exists(rp_path):
        abort(400, description="Input files not found. Please upload again.")

    try:
        tiempos_proceso = read_matrix_any_delim(tp_path, cast=float, minus_one=False)
        rutas_produccion = read_matrix_any_delim(rp_path, cast=int, minus_one=True)
    except Exception as e:
        abort(400, description=f"Could not parse uploaded files: {e}")

    # --- Apply rule ---
    if regla == 'spt':
        Cmax, resultado = reglas.spt_rule(tiempos_proceso, rutas_produccion)
    elif regla == 'mwkr':
        Cmax, resultado = reglas.mwkr_rule(tiempos_proceso, rutas_produccion)
    else:
        abort(400, description=f"Regla desconocida: {regla}")

    # --- Clean old Gantt files in static ---
    for fn in os.listdir(STATIC_DIR):
        if fn.startswith('gantt_') and fn.endswith('.html'):
            try:
                os.remove(os.path.join(STATIC_DIR, fn))
            except OSError:
                pass

    # --- Save Plotly HTML into static and serve it as a plain file ---
    filename = f"gantt_{Cmax:g}.html"  # avoids trailing .0
    fullpath = os.path.join(STATIC_DIR, filename)

    gantt_chart = reglas.imprime_gantt(rutas_produccion, resultado)
    # include_plotlyjs='cdn' makes the file smaller and avoids bundling JS
    gantt_chart.write_html(fullpath, include_plotlyjs='cdn', full_html=True)

    # Serve raw file (no Jinja -> no conflicts with {{ }} in JS)
    return send_from_directory(STATIC_DIR, filename)

@app.route('/borrarArchivos', methods=['GET', 'POST'])
def borar_archivos():
    removed = 0
    for document in os.listdir(STATIC_DIR):
        if not document.startswith('style'):  # keep your CSS
            try:
                os.remove(os.path.join(STATIC_DIR, document))
                removed += 1
            except OSError:
                pass
    return f'Archivos de texto borrados correctamente. Eliminados: {removed}'

if __name__ == '__main__':
    # Enable reloader during local dev if you want:
    # app.run(debug=True)
    app.run()
