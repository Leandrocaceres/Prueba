# Fathia · Archivo de campaña

Aplicación web local en español para consultar y ampliar el canon de Fathia,
la campaña de Anima: Beyond Fantasy. Python 3.10 o superior, sin dependencias externas.

## Descargar el proyecto completo

[Descargar Fathia-proyecto.zip](https://github.com/Leandrocaceres/Prueba/raw/refs/heads/main/Fathia-proyecto.zip)

El paquete incluye el código, la campaña actual, el canon, todos los retratos
y un archivo `COMO_ABRIR.txt` con los pasos para ejecutarlo. Extrae el ZIP completo
antes de iniciar la aplicación. Requiere Python 3.10 o superior.

## Ejecutar

Desde la carpeta del repositorio:

```sh
python3 importar_fathia.py
python3 app.py
```

La importación incorpora el documento maestro y la continuación: 20 personajes,
12 residentes del caserón, 27 vínculos, 17 entradas de mundo y reglas, seis secretos,
16 acontecimientos del documento y una escena registrada de Asuka y Enzi.
La aclaración posterior del usuario establece que todos los personajes registrados
son controlados por jugadores.

Puedes repetir la importación: registra qué versiones ya se incorporaron y no
repite entradas ni sobrescribe posteriores ediciones o eliminaciones. Actualiza
las versiones iniciales incompletas y hace un respaldo antes de cada carga nueva.
Si encuentra un personaje homónimo en una campaña sin registro de importación,
se detiene para evitar sobrescribirlo: no borres tus datos para forzar la carga.

En tu computadora, abre `http://127.0.0.1:8000` en el navegador.
Para otro puerto: `python3 app.py --port 8001`.
En el entorno en la nube, el acceso visual depende de las herramientas del entorno;
las solicitudes locales permiten validar el servicio.

## Consultar y editar

Todas las secciones muestran directamente las entradas existentes, sin formularios
de creación. El editor solo se abre al pulsar «Editar» y se cierra al guardar
o cancelar.

- **Personajes:** historias, apariencias, reglas, identidades, residencia y control.
  El filtro del caserón muestra sus 12 residentes. Buscar «victor» encuentra tanto
  la ficha de Enzi como las historias que mencionan esa identidad, sin exigir tildes.
  La ficha de Enzi tiene un selector para alternar los retratos de Enzi, Enmy y
  Víctor sin crear personajes separados. Las identidades sin archivo muestran
  un aviso en lugar de usar la imagen de otra forma. La selección se conserva
  al filtrar durante la sesión de la página. Enzi, Enmy y Víctor tienen sus retratos propios.
- **Relaciones:** tipo, grado de confirmación y nombre utilizado en cada vínculo.
  Enmy y Víctor pertenecen a Enzi; no se cuentan como personajes adicionales.
- **Acontecimientos:** los puntos 7–16 tienen orden relativo no confirmado y no se
  inventan fechas. El listado se muestra por orden de registro, no como una línea
  temporal definitiva. La escena del té se conserva fuera de la cronología confirmada.
- **Mundo y canon:** Fathia, lugares, organizaciones, reglas narrativas y visuales,
  novela visual, bot narrador y datos aún no definidos. Los antecedentes creativos
  no se convierten automáticamente en acontecimientos oficiales de la partida.
- **Secretos:** hechos y quiénes los desconocen. El archivo contiene toda la
  información del director; no ofrece una vista filtrada para jugadores.
- **Exportar JSON:** descarga todas las secciones y sus campos actuales.

La aplicación organiza los datos escritos: no usa IA ni genera narraciones.
No decide diálogos, acciones ni relaciones por los jugadores.

## Fuentes y continuidad

`canon/fathia.md` reúne el documento y la continuación, con encabezados de consulta
y la aclaración posterior sobre el control de los personajes en el apartado 27.
Se puede leer desde «Leer documento maestro» en la aplicación.

`canon/fathia-parte-inicial.md` conserva la primera entrega tal como llegó, incluido
el corte del punto 8. `canon/fathia-continuacion-original.txt` conserva el texto del
archivo adjunto sin reorganizar. Estos originales son históricos, no sustituyen
la versión integrada ni sus correcciones.

Las correcciones posteriores del usuario prevalecen. La importación actual no es
un importador universal de texto: las nuevas entregas requieren integrar su contenido
expresamente, respetando las ediciones guardadas. Antes de narrar o crear contenido,
consulta el documento maestro y las correcciones de las fichas actuales. Las imágenes originales se guardan en `imagenes/` y se asocian mediante
`imagenes/referencias.json`. Las fichas muestran la imagen completa y permiten
abrirla en su tamaño original. Los 20 personajes registrados tienen imágenes
asociadas en la carpeta `imagenes/`, conservando sus archivos originales.
Mary y Mimy comparten una misma imagen, manteniendo sus fichas separadas.
Enmy y Víctor tienen sus retratos en el selector de Enzi. Todos los personajes
y sus identidades registradas cuentan con imagen. Consulta `imagenes/README.md`.

## Datos y respaldo

SQLite guarda automáticamente en `datos/campana.sqlite3`, ignorado por Git.
Los respaldos previos a cada importación están en `datos/respaldos/`.
Para un respaldo restaurable, detén la aplicación y copia el archivo SQLite.
Para restaurarlo, con la aplicación detenida, devuelve la copia a la misma ruta.
Puedes elegir otra base con `ROL_DB`; tanto el importador como la aplicación usan
esa variable. El JSON exportado es legible y compartible; no hay importador JSON.
Eliminar un personaje elimina también sus relaciones.

Diseñada para uso local individual; no incluye cuentas ni despliegue público.

## Verificación

```sh
python3 -m unittest discover -s tests -v
```

Las pruebas usan bases temporales. Verifican fidelidad del canon, secretos,
relaciones, migración, respaldo, ausencia de duplicados, protección de correcciones,
consulta HTTP, edición, exportación y persistencia al reiniciar el servidor.
La prueba HTTP requiere permiso para abrir un socket local.
