# La Pulpería

Juego en Python + pygame-ce. No necesita archivos extra (todo se dibuja por código).

## Requisitos
- Python 3.10 o superior (python.org; en Windows marca "Add python.exe to PATH").

## Correrlo
- **Windows:** doble clic en `iniciar.bat`. La primera vez crea `.venv` e instala pygame-ce; las siguientes abre directo.
- **Mac/Linux:** `./iniciar.sh`

### Manual
```
python -m venv .venv
.venv\Scripts\activate        (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python main.py
```

## Controles
- REPORTE (OPCIONES > EXTRAS > REPORTE DE PROGRESO; ESC vuelve a EXTRAS), para el profesor o los papás: tabla de cada
  partida guardada (HISTORIA y LIBRE por aparte; < > cambia de una a otra) con la FACTURA y SOLO las opciones del MODO DE JUEGO que
  están activadas (p. ej. fracciones y multiplicar): ACIERTOS, ERRORES y %
  de aciertos con una barrita (verde 70 % o más, amarilla 40-69 %, roja
  menos de 40 %), y cuántas veces se compró la CALCULADORA. ENTER guarda
  la tabla como archivo CSV (reporte_<nombre>_<modo>.csv, en la carpeta
  del juego; se abre con Excel). Se
  guarda con la partida y empieza de cero en una partida nueva; el tutorial
  no cuenta. Qué cuenta en cada opción: ver estadisticas.py.
- NOMBRE DEL CARTEL: el niño escoge cómo se llama SU pulpería (hasta 20
  letras, números y espacios). En MODO HISTORIA, después de escoger las
  mascotas con Doña Rosa; en MODO LIBRE, al empezar la partida. Mientras
  escribe se ve el cartel en grande; ENTER: listo (vacío = LA PULPERIA).
  El cartel del techo se acomoda solo al nombre: crece a lo ancho y, si
  hace falta, la letra se achica o va en dos renglones (zonas.py,
  dibujar_cartel). Se guarda con cada partida. El menú siempre dice LA
  PULPERÍA.
- MENÚ: JUGAR, CONTINUAR, OPCIONES, AYUDA y SALIR. JUGAR empieza una
  partida NUEVA DE CERO (tienda, bodega, muebles, saldo, ropa, día 1). Antes,
  JUGAR pregunta "¿CÓMO QUIERES JUGAR?": HISTORIA o LIBRE; si ya hay una
  partida de ESE modo, pregunta "¿PARTIDA NUEVA?" (SÍ / NO). La del otro
  modo no se toca. CONTINUAR sigue la partida guardada; si hay de los dos
  modos, pregunta "¿CUÁL PARTIDA?" (HISTORIA o LIBRE, con nombre y día).
- MODO HISTORIA (historia.py): Doña Rosa, la dueña, te deja la pulpería.
  Al empezar cada día saluda (el día 1 es la bienvenida) y dice la META
  DEL DÍA con un dibujito; la meta y cuánto llevas se ven debajo del reloj
  (se pone verde con un check al cumplirla). Al terminar el turno (botón
  "DÍA N >" del cierre) se despide siempre con el nombre del jugador y da
  una pista del día siguiente. Si no se cumple la meta, se avanza igual.
  Días 1-7: atender 3 clientes, vender ₡30, pedir al camión, llamar a
  Tavo, entregar una receta (si las recetas están apagadas: atender 5),
  que no se vaya ningún cliente y vender ₡60 (final: "¡La pulpería es
  tuya!"). Desde el día 8 los saludos y metas se repiten en ronda.
  Al empezar el día 8 sube la dificultad un nivel y al empezar el día 16
  otro más (hasta AVANZADO). Una partida nueva vuelve a la dificultad de
  OPCIONES. ENTER: siguiente página; ESC: saltar el diálogo.
  Apenas se cumple la meta, Doña Rosa felicita: "¡Muy bien, Ana! Cumpliste
  la meta. Ahora solo falta terminar el día." (la de "que no se vaya
  nadie" solo se sabe al final del día).
- La pulpería abre a las 8:00 a. m. y el PRIMER CLIENTE llega a las 8:30
  (HORA_PRIMER_CLIENTE en clientes.py).
- HORARIO: el día va de 8:00 a. m. a 8:00 p. m. y dura 7 minutos reales
  (una hora = 35 segundos). Se atiende a los clientes de 8:00 a. m. a
  6:00 p. m. (el primero llega a las 8:30). A las 6:00 p. m. la tienda cierra
  sola (letrero CERRADO; los que quedaban se van) y de 6:00 a 8:00 p. m. es
  para acomodar la mercadería. En el letrero: "E: TERMINAR EL DÍA" para
  terminar antes; a las 8:00 p. m. llega el cierre de caja solo. NO hay
  límite de clientes por día: siguen llegando (cada 20-70 minutos del
  juego) hasta las 6:00 p. m. Tavo
  puede venir hasta las 5:00 p. m. (mínimo 3 horas, hasta las 8). Ajustes
  en horario.py (HORA_INICIO, HORA_CIERRE_TIENDA, HORA_FIN, DURACION_DIA).
- PARTIDA NUEVA: se empieza en la ACERA, frente a la tienda ("SUBE POR EL
  CAMINO PARA ENTRAR A LA TIENDA"). Hasta que el pulpero entra no llega
  ningún cliente y el reloj no corre.
- MODO HISTORIA: al empezar, Doña Rosa saluda y pregunta "¿Quién quieres que
  te acompañe?": LOS DOS, CANELA, BRUNO o NINGUNO (flechas + ENTER). Eso
  cambia OPCIONES > EXTRAS > MASCOTAS. En el modo LIBRE Doña Rosa no aparece
  nunca (las mascotas son las de OPCIONES > EXTRAS).
- CLIENTES: hacen FILA del lado de arriba del mostrador, a lo largo de él: el
  primero frente a la CAJA y los demás hacia la izquierda (mirando al
  mostrador). Si se mueve el mostrador (SHIFT+E), la fila lo sigue: al
  soltarlo, los clientes caminan a su nuevo frente (clientes.py,
  lugares_del_mostrador). Hasta 2 en principiante, 4 en
  intermedio y 6 en avanzado (clientes_en_fila en niveles.py). Solo el del
  frente dice su pedido; los de la fila esperan sin globo y avanzan un
  lugar cuando el de adelante se va. Entre un cliente y el siguiente pasan
  de 20 a 70 minutos del reloj (al azar); si se atendió a alguien, ese
  tiempo empieza cuando ya salió por completo de la tienda.
  Ajustes en clientes.py (MINUTOS_ENTRE_CLIENTES, LUGARES)
- Datos de arriba (reloj, meta, saldo, día): recuadro gris con letra
  amarilla (HUD_FONDO / HUD_LETRA en main.py).
- OPCIONES, en este orden: SONIDO, GRÁFICOS, DIFICULTAD (izquierda/derecha:
  principiante, intermedio, avanzado), MODO DE JUEGO, EXTRAS y TUTORIAL.
- OPCIONES > EXTRAS: dos botones SÍ/NO.
  MASCOTAS: apaga todo el sistema de mascotas (Canela, Bruno, la casa de
  Canela, su comida en las cuentas y la persecución). Si está en SÍ, debajo
  se elige CUÁLES: Canela y Bruno, solo Canela o solo Bruno.
  PERSONALIZACIÓN: apaga el armario de la bodega y toda la ropa (nadie la
  lleva puesta). Lo comprado no se pierde: vuelve al encenderla.
  De entrada: MASCOTAS en SÍ con solo Canela, y PERSONALIZACIÓN en NO.
  REPORTE DE PROGRESO (ENTER: VER): la tabla para el profe o los papás.
  Se guardan con la partida. Código en main.py (EXTRAS, aplicar_extras)
- ARMARIO: más de 200 artículos; casi todos vienen en muchos colores
  (gorras, gorros, boinas, lentes, corbatines, corbatas, bufandas, camisas,
  delantales, pelajes, collares, moños, suéteres, impermeables, pañoletas).
  Cada renglón muestra un cuadrito con su color y la lista se desplaza
  con las flechas (ordenada de NORMAL a DE LUJO). En cosmeticos.py (_agregar)
- Preguntas (¿PARTIDA NUEVA?): la opción escogida es la oscura.
- TUTORIAL (14 pasos, siempre el mismo): al empezar una partida nueva, después
  de elegir HISTORIA o LIBRE, el juego pregunta "¿JUGAR EL TUTORIAL?" (SÍ de
  entrada la primera vez). También en OPCIONES > TUTORIAL. Doña Rosa llega y
  pide 2 manzanas y un letrero con flecha explica: caminar, tomar en la
  góndola, dejar en el mostrador, cobrar en la caja (contar los dibujos; C:
  calculadora con costo), ver las ventas (H), el libro de recetas (R) y las
  recetas con mitad / tercio / cuarto, ir a la BODEGA y volver, el TELÉFONO
  para pedir al camión y el horario (6 p. m. cierre, TERMINAR EL DÍA). Los
  pasos que solo explican se pasan con ENTER. TAB lo salta. Al terminar
  empieza el día 1 (en HISTORIA, ahí aparece Doña Rosa). Pasos en tutorial.py
- AYUDA: pantalla con todos los controles del juego.
- OPCIONES > SONIDO: MÚSICA DEL MENÚ (alegre de 8 bits, que viene de
  entrada, marimba o tranquila) y MÚSICA DE LA TIENDA, la que suena
  mientras se juega. ACTIVAS, rápidas y con ritmo para animar: marimba
  alegre (viene de entrada), cumbia, 8 bits saltarín y alegre (8 bits).
  TRANQUILAS: piano tranquilo, guitarra suave, marimba suave o cajita de
  música. Las activas se generan con herramientas/gen_musica_activa.py.
  Cada estilo tiene 3 canciones distintas que se alternan en desorden, sin
  repetir la misma dos veces seguidas. Además: volumen, efectos
  especiales (cobrar, abrir caja, tomar, dejar, acierto, error, campanita del
  cliente, timbre del ayudante, logro) y ruido de fondo (viento y carros
  afuera, grillos de noche). Los tres volúmenes vienen en 3 (de 10). Al
  cambiar algo suena una prueba. Los audios
  están en la carpeta "sonidos"; se generan con herramientas/gen_sonidos.py
  y herramientas/gen_musica_tienda.py (necesitan numpy, scipy y ffmpeg; no
  hace falta para jugar).
- OPCIONES > GRÁFICOS: tipo de letra (escolar, que viene de entrada,
  sencilla, redonda, clásica, máquina y moderna; todas se ajustan al mismo
  tamaño; usa las fuentes de Windows y, si falta alguna, una
  parecida), luciérnagas sí/no, AVISOS DE ABAJO sí/no (el texto de abajo
  que dice con qué interactuar), y el color de paredes, piso,
  alfombras, mostrador, refrigeradoras y muebles (flechas izquierda/derecha).
  Los colores se aplican en la tienda y en la bodega. Todo viene en
  ORIGINAL; hay una vista previa y un botón para volver a los
  colores originales. Colores en interior.py (OPCIONES_COLOR), letras en
  fuentes.py (TIPOS)
- OPCIONES > MODO DE JUEGO: activar o apagar cada tipo de problema, en orden
  alfabético (multiplicar cantidad x precio y sumar el total de la factura
  siempre están): adivinanzas de colores, contar en la factura, fracciones
  de recetas (mitad, tercio), multiplicar recetas (doble, triple), paciencia
  de los clientes, recordar el pedido (se esconde a los 5 s en principiante
  y avanzado, 8 s en intermedio; P lo repite), sucesiones de los clientes frecuentes (si se apaga, los
  disfrazados siguen viniendo, pero como clientes normales que piden una
  receta al azar), suma del cierre de caja y vuelto.
  Vienen APAGADOS de entrada: adivinanzas de colores, multiplicar recetas,
  paciencia de los clientes, sucesiones y suma del cierre de caja. Lista, textos y lo que viene
  apagado en modos.py (APAGADOS)

- Menú: flechas + ENTER ("JUGAR"). Antes de empezar se elige personaje
  (flechas izquierda/derecha + ENTER) y se escribe el nombre del niño o niña. En OPCIONES se elige la dificultad
  (principiante, intermedio, avanzado; se ajusta en niveles.py)
- Caminar: flechas / WASD. ESC abre el menú de PAUSA (el juego se detiene):
  SEGUIR JUGANDO, AYUDA (al cerrarla vuelve al juego) o SALIR AL MENÚ
  (guarda la partida). Código en main.py (OPCIONES_PAUSA, draw_pausa)
- SALDO (arriba a la derecha, con una monedita): empieza en ₡50; suben las
  ventas y bajan los pedidos al camión, el pago a Tavo y lo que se compra
  en el armario. Si no alcanza, el teléfono y el armario dicen "No te
  alcanza". En H se ve el saldo. Ajuste: SALDO_INICIAL en main.py
- ARMARIO (en la bodega, pared derecha; E junto a él): 52 artículos en 8
  categorías. Pulpero/pulpera: sombreros, lentes, cuello, camisas y
  delantales. Canela: pelaje, collares y gorros. Cada artículo tiene un
  estilo: NORMAL (₡30-₡80), LLAMATIVO (₡80-₡180) o DE LUJO (₡200-₡400, hay
  que ahorrar varios días). Izquierda/derecha: categoría; arriba/abajo:
  artículo; ENTER: comprar, poner o quitar. Se compra una vez; el
  probador de la derecha muestra cómo se ve antes de comprar. Catálogo y
  precios en cosmeticos.py (ARTICULOS)
- BRUNO, EL PERRO DE LA PULPERÍA (opcional, como Canela): pasea por la
  tienda, a veces sale a echarse a dormir en la acera junto a la puerta y
  vuelve a entrar. E junto a él: "¡Guau!". En el armario tiene pelaje,
  collares (pañoleta, picos, dorado...) y TRAJES: suéter, impermeable,
  dinosaurio verde o morado, abejita, tiburón, superhéroe y unicornio.
  Comportamiento y dibujos en perro.py
- PERSECUCIÓN: con las dos mascotas, de vez en cuando (cada 35 a 80
  segundos, cuando se encuentran cerca) Bruno persigue a Canela por los
  pasillos de la tienda: ella bufa ("¡Fsss!", siempre visible; el globo de
  Bruno se sube para no taparlo) y él ladra; al final cada uno
  se sienta a descansar. Ajustes en persecucion.py
- CASA DE CANELA (abajo a la derecha de la tienda; E junto a ella): empieza
  como una caja de cartón y se mejora a cama acolchada (₡250), casita de
  madera (₡600) y castillo de gato (₡1200). Canela a veces se va a dormir
  ahí: en la caja y la cama queda tapada por el frente y solo se le ven las
  orejas; en la casita y el castillo, las orejas asoman por la puerta.
  Precios en casa_gato.py (NIVELES, CAMA_Y)
- CUENTAS DEL DÍA: al cerrar cada día se pagan luz (₡8), agua (₡5),
  alquiler (₡20), comida de Canela (₡4) y comida de Bruno (₡5) (solo las
  de las mascotas que haya); en el cierre de caja salen con
  dibujitos y el saldo que queda. Montos en main.py (CUENTAS_DIA)
- HARINA: saco naranja con harina blanca y una espiga (pixel art en
  imagenes/harina.png; de cerca se ve tal cual, en los estantes una
  versión chica hecha a mano en productos.py).
- HELADERA: en L con el mostrador (baja desde la huevera). Tiene 8
  helados de PALETA (₡3) arriba y 8 de CONO (₡4) abajo; solo acepta
  helados ("¡Los helados se derriten!" si se intenta en otro mueble). En la
  bodega hay un congelador con 16 de cada uno, y se piden por teléfono en
  la pestaña HELADOS. Pixel art en imagenes/paleta.png y cono.png;
  posiciones en interior.py (heladera_slots) y zonas.py (CONGELADOR_BODEGA).
  Una partida guardada antes de la heladera la tiene vacía: se llena
  pidiendo helados al camión.
- BEBIDAS y LECHE en pixel art (imagenes/agua.png, naranjada.png,
  fresa.png, cola.png, limonada.png y leche.png); en refris y globos van
  versiones chicas (productos.py, SPRITES_BEBIDA). Naranjada y leche son
  los pixel art que pasó el equipo; agua, fresa, cola (sin marca) y
  limonada (en vaso) están dibujados para el juego, porque las imágenes de
  referencia tenían marca de agua, logo de una app o una marca real.
- ZANAHORIA, BRÓCOLI, ELOTE y HUEVO: igual que la harina, en
  imagenes/zanahoria.png, brocoli.png, elote.png y huevo.png (de cerca tal
  cual; chicos en productos.py, COLORES_PROPIOS). Zanahoria y brócoli son
  los pixel art que pasó el equipo; elote y huevo están dibujados para el
  juego (las imágenes de referencia tenían marca de agua de Dreamstime).
- MOSTRADOR: la balanza va a la izquierda y el libro, el teléfono y la caja
  a la derecha. En el centro hay una cuadrícula de 3 filas x 12 casillas
  (36): cada producto ocupa su casilla y ninguno queda escondido detrás de
  otro. Ajustes en interior.py (MOSTRADOR_X, MOSTRADOR_BASES, MOSTRADOR_COLS)
- MENÚ: de fondo se ve la misma pulpería del juego (con Canela en el techo).
- GUARDAR PARTIDA: se guarda sola al cerrar el juego, al volver al menú
  (ESC), al empezar cada día y cada 20 segundos mientras se juega. Al
  abrir otra vez, CONTINUAR sigue donde se quedó: día, saldo, ventas,
  productos, muebles, bodega, pedido del camión y ropa. MODO HISTORIA y
  MODO LIBRE tienen cada uno SU partida, independientes: jugar una no
  cambia la otra. Archivos, junto al juego: partida_historia.json,
  partida_libre.json y ajustes.json (los ajustes de OPCIONES, para las
  dos). Borrar uno = empezar ese modo de cero. Un partida_guardada.json
  de una versión anterior se pasa solo al archivo de su modo.
- CANELA, LA GATA DE LA PULPERÍA: pasea por los pasillos y se sienta a
  mover la cola; de vez en cuando sale por la puerta, sube al techo de la
  pulpería (se ve desde la calle), toma una siesta y vuelve a entrar. E
  junto a ella: se deja acariciar. Comportamiento en mascota.py
- Al cobrar, la factura se cierra de una vez (ya no sale la pantalla de
  "venta cobrada").
- BODEGA: 3 columnas de 3 repisas de varilla de metal, de 3 pisos cada
  una; cada piso guarda 8 unidades de un producto. Columna 1: frutas y
  columna 2: verduras (en canastos); columna 3: abarrotes y leche. Al fondo,
  dos refris de gaseosas (3 pisos de 8 botellas) y una huevera grande
  (32 huevos). Distribución en zonas.py (CONTENIDO_REPISAS, REFRIS_BODEGA)
- E: frente a una refri, góndola, el mostrador o un estante de bodega abre la
  vista de cerca del mueble: clic en el producto para tomarlo (o flechas + E).
  ESC cierra. Máximo 3 en las manos / dejarlo en el mostrador /
  acomodar productos de la bodega en góndolas y refris
- PEDIDO POR TELÉFONO: el teléfono rojo del mostrador (E o clic) abre el
  pedido (solo hasta las 2:00 p. m.). Los productos van en pestañas por
  tipo (abarrotes, bebidas, frutas, huevos y leche, verduras; todo en orden
  alfabético). Columnas: EN TIENDA (lo que hay / lo máximo que cabe, entre
  la tienda y la bodega), COMPRAR (cajas) y PRECIO. Todas las cajas traen 3
  unidades y el camión trae máximo 8 cajas (las que caben en la acera). Ya
  viene sugerido lo que más falta. Solo se
  puede pedir una caja si TODO lo que trae cabe entre la tienda (góndolas,
  refris, estante, huevera) y la bodega; lo que ya está en cajas afuera
  también ocupa lugar. Si no cabe, avisa cuántos lugares quedan. Cuesta un poco menos que el precio de
  venta y se ve en el historial (H). Unas 2 horas después llega el camión por
  la calle, se estaciona en el costado izquierdo de la tienda, deja las cajas
  en la acera y se va. Junto a una caja: E abre su menú (tomar 1 o llenar las
  manos) y se lleva directo a los muebles de la tienda. Si Tavo está
  trabajando, primero mete lo de las cajas a la bodega. Caja vacía: desaparece.
  Ajustes en camion.py
- AYUDANTE (Tavo): botón en la pared derecha, junto al mostrador (E). Dice
  cuántas horas puede trabajar (de 3 a 8, según el día y la hora en que se le
  llama, sin pasarse de las 8:00 p. m.; si quedan menos de 3 horas, no viene). Mientras trabaja trae productos de la
  bodega y llena los huecos de góndolas, refris, estante y huevera. Lleva
  hasta 3 productos en las manos; si el carrito está libre (nadie lo empuja
  y está vacío), lo usa y lleva hasta 8. Si el pulpero lo necesita, ESPACIO
  junto a Tavo: se lo presta y sigue con las manos. Al
  terminar su turno (o el día) dice "Hoy trabajé X horas y son 3 colones la
  hora": E junto a él y el niño escribe cuánto pagarle (con pistas). El pago
  se ve en el historial (H). Una vez por día. Si hay un pedido del camión
  en camino o cajas afuera cuando llega su hora de salida, se queda a
  guardarlo y cobra horas extra (completas): a 3 colones si el camión ya
  había llegado en su turno, a 5 si llega después de su hora de salida.
  Ajustes en ayudante.py (PAGO_POR_HORA, PAGO_EXTRA_TARDE)
- CARRITO DE COMPRAS: está estacionado en la sala, cerca de la puerta de la
  bodega. ESPACIO junto a él: empujarlo (va adelante, hacia donde miras).
  Con el carrito se llevan hasta 8 productos en vez de 3; se toman, acomodan
  y devuelven igual que con las manos. ESPACIO otra vez: soltarlo (los
  productos se quedan adentro). No sale a la calle: se queda en la tienda.
  Ajustes en carrito.py (CAPACIDAD)
- Q: devolver el último producto tomado (a su lugar, si es el mismo estante)
- Clientes: entran, dicen su pedido y esperan detrás del mostrador.
  Los diálogos son cortos: saludo + "¿me regala...?", "¿me das...?" o
  "quiero..." + la orden. Los productos no se nombran: salen como
  "2x" + el dibujo del producto (en el texto se escriben "[2:banano]").
  Las recetas sí se dicen en palabras ("¿Me das los ingredientes para
  medio queque?"), igual que las adivinanzas de colores. Los frecuentes
  dicen su regla corta ("Cada día compro el doble de aguas.").
  Junta su pedido en el mostrador y abre la caja. P: el cliente repite el pedido
  (hasta 2 veces). En OPCIONES > MODO DE JUEGO se activa la PACIENCIA DE LOS CLIENTES
  (viene desactivada): con ella, cada cliente tiene una barrita y si no lo
  atiendes a tiempo se va molesto. Los segundos se ajustan en niveles.py
- CLIENTES FRECUENTES (razonamiento inductivo y deductivo). Cada uno dice su
  regla: Payaso Pepín (bananos, uno más que ayer), Bombera Ana (aguas, el
  doble que ayer), Chef Tito (huevos, la mitad que ayer), Astronauta Leo
  (leches, 1 y 2 alternados) y Capitana Perla (naranjas, una menos que ayer).
  Vienen una vez al día, siempre por lo mismo, y nunca dos seguidos. Algunos
  días dicen cuántos quieren; otros solo dicen la regla y lo que compraron
  ayer; y algún día "no se acuerdan" y solo dicen lo de ayer (nunca el primer
  día, cambia cada semana y puede pasar varias veces). Máximo 8. Cada 7 días
  empiezan de nuevo. Cada día: 5 frecuentes + 4 clientes normales = 9.
  Cada mañana llega el camión y la bodega se llena otra vez.
  Ajustes en clientes.py (FRECUENTES); disfraces en disfraces.py
- H: historial con el monto de cada venta del día (sin el total) y, arriba,
  las caritas de clientes atendidos (feliz) y los que se fueron (triste).
  Esos números ya no salen en la pantalla del juego; tampoco el texto
  "TIENDA ABIERTA/CERRADA" (eso lo dice el letrero de la puerta).
- El aviso de abajo (con qué interactuar) se puede apagar en GRÁFICOS.
  Arriba a la derecha solo se ve el día. Al final del día llega el CIERRE DE CAJA, casi sin texto: caritas
  con los clientes atendidos (feliz) y los que se fueron (triste), las
  ventas como una suma (₡3 + ₡8 + ₡14 = ___) y la casilla del total. Las
  pistas son solo números ("3 + 8 = ?"). Luego, botón "DÍA 2 >" (ENTER o clic)
- Abrir/cerrar la tienda: acércate al letrero ABIERTO/CERRADO junto a la puerta
  (adentro o en la calle) y pulsa E. Cerrada: no entran clientes nuevos y el
  reloj se detiene; útil para llenar la mercadería
- Luciérnagas: salen después de las 3:00 p. m. (adentro y en la calle);
  de noche brillan más. Hora en main.py (HORA_LUCIERNAGAS).
  Ajustes en luciernagas.py (CANTIDAD, VELOCIDAD)
- Afuera hay un poste de luz que se enciende de noche, y de noche salen
  más luciérnagas entre los árboles. Ajustes en ambiente.py (POSTE)
- Calle con vida: personas que saludan, autos (frenan si estás en la calle),
  perros, gatos y pájaros. Ajustes en ambiente.py
- Día y noche: el reloj (arriba a la izquierda) corre parejo, también
  mientras atiendes (ver HORARIO). A las 6:00 p. m. la tienda cierra aunque
  haya clientes: se cierra la factura, los que estaban se retiran (no
  cuentan como perdidos) y ya no llegan más.
  Por las ventanas del frente entra el sol: rayos largos y dorados en la
  mañana, cortos y blancos a mediodía, anaranjados en la tarde y nada de
  noche. Ajustes en horario.py (SEGUNDOS_POR_CLIENTE, VENTANAS_FRENTE)
- E frente a la caja (con las manos vacías): el cliente revisa su pedido y,
  si está bien, se abre la factura
- VUELTO: en la factura, debajo del total, aparece con cuánto paga el cliente
  (billetes de 1, 2, 5, 10 y 20; solo se dice la suma) y el niño escribe el
  vuelto. Se activa o desactiva en OPCIONES > MODO DE JUEGO (
  viene activado). Con errores da pistas ("cuenta desde 13 hasta 16")
- BURBUJAS DE AYUDA (tooltips): la opción marcada muestra una burbuja
  oscura que dice qué hace: menú principal, pausa, SONIDO, GRÁFICOS,
  EXTRAS, el botón HACER PEDIDO del teléfono y, en la factura, COBRAR,
  CANCELAR y la calculadora ("Para usar la calculadora cuesta ₡5. Solo
  sirve para esta factura") al pasar el mouse. Con el mouse sobre el reloj,
  la meta, el saldo o el día también se explica cada dato. Textos en
  main.py (TOOLTIP_MENU, TOOLTIP_SONIDO, TOOLTIP_VISUAL, TOOLTIP_EXTRAS...).
  Se pueden apagar en OPCIONES > GRÁFICOS > BURBUJAS DE AYUDA (vienen
  activadas; se guarda con la partida).
- PANTALLA COMPLETA: el juego arranca llenando toda la pantalla (sin
  deformarse; si el monitor es más alto o más ancho, quedan franjas negras).
  F11 (o ALT + ENTER) cambia entre pantalla completa y ventana; la ventana
  se puede agrandar o maximizar. También en OPCIONES > GRÁFICOS > PANTALLA
  COMPLETA. En Windows con la pantalla agrandada (125 %, 150 %...) se ve
  nítido. Código en main.py (crear_ventana, presentar).
- ALFOMBRA DE LA CALLE: centrada en el pasillo entre la góndola de abajo y
  la heladera (zonas.py, PUERTA_SALA_X). Por ahí entran y salen el jugador,
  los clientes, Tavo y las mascotas.
- Factura: cada fila muestra solo los DIBUJOS del producto (grandes),
  la cantidad y el precio ("3 x ₡5 ="), sin el nombre escrito.
- RECETAS CON CONVERSACIÓN: la mitad de los clientes que piden receta no
  la saben: "¡Buenos días, Ana! Quiero hacer vaca negra. ¿Me puedes
  ayudar?" → el pulpero responde con su globo "¡Claro que sí! Una receta
  lleva 4 [cono] y 4 [cola]." → "¡Perfecto! Quiero media vaca negra." Los
  otros ya la saben y piden directo ("Ya sé la receta: quiero un cuarto de
  vaca negra"). Después de la conversación el cliente SIEMPRE pide una
  fracción (medio, tercio o cuarto, según lo que permita la receta).
  Mientras conversan no baja la paciencia. Ajustes en
  clientes.py (PROB_CONVERSACION, SEGUNDOS_PASO). Ahora también se pide UN
  CUARTO (÷ 4) en las recetas que lo permiten: vaca negra, banana split
  (4 bananos + 4 conos) y licuado (4 bananos + 4 leches).
- Factura: números + ENTER. Con errores aparecen pistas; después de 2, 3 o
  4 errores (según el nivel) se recuerda que se puede COMPRAR la
  calculadora (clic en ella o ESPACIO para usarla con el teclado).
  CALCULADORA CON PAGO: en la factura hay un botón con una calculadita y
  su precio; con C (o clic) se paga y aparece desde el principio. Cuesta
  ₡5 en principiante, ₡10 en intermedio y ₡15 en avanzado
  (precio_calculadora en niveles.py). Sirve SOLO para esa factura: al
  salir de la caja y volver a entrar, está bloqueada otra vez. El gasto
  queda en el historial (H). Si no alcanza el saldo, el botón se ve gris.
  La calculadora es SOLO DE PAGO: ya no aparece gratis con los errores.
- SHIFT+E: mover muebles (el estante de abarrotes de la pared es fijo). Un
  mueble no se puede mover ni soltar encima de un personaje (tú, clientes,
  Tavo) ni del carrito
- Abarrotes: el estante de la pared (arriba a la derecha) tiene harina,
  azúcar, arroz y frijoles. La refri de la derecha es solo de leches y aguas.
  Las frutas y verduras van en canastos, uno por producto (6 piezas cada uno).
  La HUEVERA (20 huevos) es el mueble a la par del mostrador. Todo se toma
  con E y se repone desde la bodega; cada producto solo va en su mueble
- LIBRO DE RECETAS: es el libro abierto sobre el mostrador. Se abre con E
  frente a él, con un clic encima o con la tecla R (también en la bodega).
  5 recetas de máximo 4 ingredientes: pan, queque, arroz con leche, gallo
  pinto y ensalada de frutas. Izquierda: ingredientes para 1 receta.
  Derecha: foto de muestra del platillo. El libro NO hace cálculos: si el
  cliente pide "medio queque" o "el doble de pan", el niño calcula
  mentalmente. Flechas: cambiar página. R o ESC: cerrar.
  Nunca piden la receta entera (esa ya está en el libro): solo la mitad, un
  tercio, el doble o el triple. Por nivel: principiante e intermedio piden la
  mitad, el doble o el triple; avanzado, además, un tercio. Las fracciones salen 4 veces más seguido
  (PESO_FRACCION en clientes.py). Solo se piden tamaños que den
  números enteros. Recetas en recetas.py; probabilidad en niveles.py.
  Son 8: pan, queque, arroz con leche, gallo pinto, ensalada de frutas
  (dibujo con la fruta picada dentro del tazón), VACA NEGRA (4 helados de
  cono + 4 colas), BANANA SPLIT (2 bananos + 4 helados de cono) y LICUADO
  DE BANANO (4 bananos + 2 leches).
- P: el cliente repite su pedido (hasta 2 veces). Si se le pide una
  tercera vez, se retira de la tienda sin decir nada. No aparece en pantalla
  para no llenarla de texto

## Nota
No uses la carpeta `.venv` del zip original: es de otra computadora (otra ruta y otro Python) y no funciona al copiarla. Además, no instales `pygame` y `pygame-ce` juntos en el mismo entorno; chocan.
