Modificaciones a realizar:
-Mover C:\Users\Jefferson\Documents\8 Semestre\Curricular\tesis\back\apps\analytics\socketio.py a shared
-Abstraer socketio a para que sea un servicio que se pueda usar en cualquier

-Flujos que se deben verificar/implementar:
-Cuando un docente crea una actividad, se debe enviar una notificacion a los alumnos que estan en la seccion de la actividad y a sus representantes.
-Cuando un docente califica una actividad, se debe enviar una notificacion a los alumnos que estan en la seccion de la actividad y a sus representantes.
-Cuando un docente crea una asistencia, se debe enviar una notificacion a los alumnos que estan en la seccion de la asistencia y a sus representantes.
-Cuando se crea un incidente de conducta, se debe enviar una notificacion a los alumnos que estan en la seccion de la actividad y a sus representantes.

-Cuando se crea un incidente de conducta, se debe debe recalcular el promedio de conducta del estudiante.
-Cuando se califica una actividad, se debe debe recalcular el promedio de conducta del estudiante.

-Tablas se debe verificar que todas las tablas intervengan como motor de datos para el calculo de riesgo, no se debe asumir que las tablas intervienen.
-Se debe vericar que realmente ese tabla este conectada en alguna parde del calculo o restriccion o que sus relaciones restringan o alimneten algo, tablas sopechosas a verificar QualitativeScaleSublevel
