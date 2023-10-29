import os
from flask import Flask, request
from flask.templating import render_template
from werkzeug.utils import secure_filename
import reglas

UPLOAD_FOLDER = 'static'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

archivo_t, archivo_r = '', ''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    
    if request.method == 'POST':
        global archivo_t, archivo_r
        if archivo_t == '' and archivo_t == '':
            tiempos = request.files["archivo_tiempos"]
            rutas = request.files["archivo_rutas"]
        
            if 'archivo_tiempos' in request.files:
                # Guardar archivo de tiempos
                archivo_t = secure_filename(tiempos.filename)
                tiempos.save(os.path.join(app.config['UPLOAD_FOLDER'], archivo_t))
                
            if 'archivo_rutas' in request.files:
                # Guardar archivo de rutas
                archivo_r = secure_filename(rutas.filename)
                rutas.save(os.path.join(app.config['UPLOAD_FOLDER'], archivo_r))

    return render_template("index.html", archivo_t=archivo_t, archivo_r=archivo_r)

@app.route('/solucion', methods=['GET', 'POST'])
def muestra_Sol():
    if request.method == 'POST':
        global archivo_t, archivo_r
        try:
            # archivo separado por tabuladores
            tiempos_proceso =  [[float(i) for i in linea.strip().split('\t')] for linea in open(UPLOAD_FOLDER+'/'+archivo_t,'r')]
        except:
            pass
        try:
            # archivo separado por comas
            tiempos_proceso =  [[float(i) for i in linea.strip().split(',')] for linea in open(UPLOAD_FOLDER+'/'+archivo_t,'r')]
        except:
            pass
        try:
            # archivo separado por espacios
            tiempos_proceso =  [[float(i) for i in linea.strip().split()] for linea in open(UPLOAD_FOLDER+'/'+archivo_t,'r')]
        except:
            pass
        try:
            # archivo separado por tabuladores
            rutas_produccion = [[int(i)-1 for i in linea.strip().split('\t')] for linea in open(UPLOAD_FOLDER+'/'+archivo_r,'r')]
        except:
            pass
        try:
            # archivo separado por comas
            rutas_produccion = [[int(i)-1 for i in linea.strip().split(',')] for linea in open(UPLOAD_FOLDER+'/'+archivo_r,'r')]
        except:
            pass
        try:
            # archivo separado por espacios
            rutas_produccion = [[int(i)-1 for i in linea.strip().split()] for linea in open(UPLOAD_FOLDER+'/'+archivo_r,'r')]
        except:
            pass
        regla = request.form['regla']
        if regla == 'spt':  
            Cmax, resultado = reglas.spt_rule(tiempos_proceso, rutas_produccion)
        elif regla == 'mwkr':
            Cmax, resultado = reglas.mwkr_rule(tiempos_proceso, rutas_produccion)
        gantt = reglas.imprime_gantt(rutas_produccion, resultado)
    return render_template("gantt.html", regla=regla)

if __name__ == '__main__':
    app.run(debug = True)