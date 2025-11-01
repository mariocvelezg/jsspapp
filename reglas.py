import plotly.express as px

def spt_rule(tiempos, rutas):
    
    # Inicializar Variable
    n = len(tiempos)                     # Número de trabajos
    m = max([len(i) for i in rutas])     # Número de máquinas
    TrabajoLibre = [0 for j in range(n)] # Tiempo en el que se libera cada trabajo
    MaquinaLibre = [0 for j in range(m)] # Tiempos en los que se libera cada máquina
    q = [0 for i in range(n)]            # Contador de operaciones programadas de cada trabajo
    SinTerminar = [i for i in range(n)]  # Trabajos sin terminar
    Gantt = []                           # Detalle del programa de producción
    Inicio_Fin = [[None for i in range(m)] for j in range(n)]
    
    t = 0
    while len(SinTerminar)>0:
    
        # Actualizar A(t): Máquinas disponibles en el instante t
        A = [maq for maq in range(m) if MaquinaLibre[maq]<=t]

        # Actualizar Um(t): Trabajos disponibles para programarse en la máquina m en el instante t
        U = [[j for j in SinTerminar if TrabajoLibre[j]<=t and rutas[j][q[j]]==m] for m in A]

        # Seleccionar el trabajo a programar en cada máquina en A
        for posicion, opciones in enumerate(U):
            if len(opciones)>0:
                if len(opciones)==1:
                    jj=opciones[0]    # jj --> índice del trabajo a programar
                else:
                    tiempos_proceso = [tiempos[trabajo][q[trabajo]] for trabajo in opciones]
                    jj = opciones[tiempos_proceso.index(min(tiempos_proceso))]  # jj --> índice del trabajo a programar (regla SPT)
    
                # Actualizar variables
                TrabajoLibre[jj] = t + tiempos[jj][q[jj]]
                MaquinaLibre[A[posicion]] = TrabajoLibre[jj]
                Gantt.append({'trabajo':jj, 'operacion':q[jj], 'inicio':t, 'fin':TrabajoLibre[jj]})
                Inicio_Fin[jj][q[jj]] = (t,TrabajoLibre[jj])
                q[jj]+=1
                if q[jj] == len(rutas[jj]):
                    SinTerminar.remove(jj)
                    if len(SinTerminar)==0:
                        return max(TrabajoLibre), Inicio_Fin
    
        # Actualizar t
        t = min([tiempo for tiempo in MaquinaLibre if tiempo>t])
        
def imprime_programa(prog):
    tabla = (10+18*len(prog[0]))*'=' + ' <br/>'
    formatString = '{:^10}' + len(prog[0])*'{:<18}'
    contentTuple = tuple(['Trabajo']) + tuple('Operación '+str(i+1) for i in range(1+len(prog[0])))
    tabla += formatString.format(*contentTuple) +  '<br/>'
    tabla += (10+18*len(prog[0]))*'=' + ' <br/>'

    #tabla += '\n'
    #n_espacios = '{:^10}' + len(prog[0])*'{:<18}' + '\n'
    #el_texto = ['Trabajo']+['Operación '+str(i+1) for i in range(1+len(prog[0]))]
    #tabla += n_espacios.format(*el_texto)
    #tabla += '\n'
    #tabla += (10+18*len(prog[0]))*'='+ '\n'
    
    # for i in range(len(prog)):
        # x = ['j'+str(i+1)]+prog[i]
        # tabla += '' + n_espacios.format(*[str(k) for k in x]) + '\n'
    # tabla += separador
    return tabla

def mwkr_rule(tiempos, rutas):
    # Inicializar Variable
    n = len(tiempos)                     # Número de trabajos
    m = max([len(i) for i in rutas])     # Número de máquinas
    TrabajoLibre = [0 for j in range(n)] # Tiempo en el que se libera cada trabajo
    MaquinaLibre = [0 for j in range(m)] # Tiempos en los que se libera cada máquina
    q = [0 for i in range(n)]            # Contador de operaciones programadas de cada trabajo
    SinTerminar = [i for i in range(n)]  # Trabajos sin terminar
    Gantt = []                           # Detalle del programa de producción
    mwkr = [sum(t) for t in tiempos]
    Inicio_Fin = [[None for i in range(m)] for j in range(n)]
    
    t = 0
    while len(SinTerminar)>0:
        
        # Actualizar A(t): Máquinas disponibles en el instante t
        A = [maq for maq in range(m) if MaquinaLibre[maq]<=t]
    
        # Actualizar Um(t): Trabajos disponibles para programarse en la máquina m en el instante t
        U = [[j for j in SinTerminar if TrabajoLibre[j]<=t and rutas[j][q[j]]==m] for m in A]
    
        # Seleccionar el trabajo a programar en cada máquina en A
        for posicion, opciones in enumerate(U):
            if len(opciones)>0:
                if len(opciones)==1:
                    jj=opciones[0]    # jj --> índice del trabajo a programar
                else:
                    work_remaining = [mwkr[trabajo] for trabajo in opciones]
                    jj = opciones[work_remaining.index(max(work_remaining))]  # jj --> índice del trabajo a programar (regla MWKR)
                # Actualizar variables
                TrabajoLibre[jj] = t + tiempos[jj][q[jj]]
                MaquinaLibre[A[posicion]] = TrabajoLibre[jj]
                mwkr[jj]-=tiempos[jj][q[jj]]
                Gantt.append({'trabajo':jj, 'operacion':q[jj], 'inicio':t, 'fin':TrabajoLibre[jj]})
                Inicio_Fin[jj][q[jj]] = (t,TrabajoLibre[jj])
                q[jj]+=1
                if q[jj]== len(rutas[jj]):
                    SinTerminar.remove(jj)
                    if len(SinTerminar)==0:
                        return max(TrabajoLibre), Inicio_Fin
        
        # Actualizar t
        t = min([tiempo for tiempo in MaquinaLibre if tiempo>t])

def imprime_gantt(rutas, prog):
    datos = dict(
        trabajo = ['j'+str(job+1) for job,fila in enumerate(prog) for op,k in enumerate(fila)],
        operacion = ['op'+str(op+1) for job,fila in enumerate(prog) for op,k in enumerate(fila)],
        inicio = [op[0] for fila in prog for op in fila],
        duracion = [op[1]-op[0] for fila in prog for op in fila],
        fin = [op[1] for fila in prog for op in fila],
        recurso = ['Máquina 0'+str(r+1) if r<9 else 'Máquina '+str(r+1) for fila in rutas for r in fila])
    print(datos)
    hovertemp="<br>".join([
        "<b>Trabajo:</b> %{customdata[0]}",
        "<b>Operación:</b> %{customdata[1]}",
        "<b>Inicio:</b> %{base}",
        "<b>Fin:</b> %{x}<extra></extra>", # <extra></extra> elimina nombre del 'trace' (hover mode)
        ])
    
    fig = px.bar(data_frame=datos,
        base='inicio',
        x='duracion',
        y='recurso',
        color='trabajo',
        custom_data=['trabajo', 'operacion'],
        orientation = 'h',
        hover_name='trabajo',
        #hover_data = {'inicio':True, 'duracion':True, 'color':False},
        range_y=(0, 3))
    fig.update_yaxes(title='', autorange="reversed", categoryorder='category ascending')
    fig.update_xaxes(title='Tiempo')
    fig.update_traces(hovertemplate=hovertemp)
    return fig
    #print('hello!!!!!')
    #fig.write_html('./templates/gantt.html')