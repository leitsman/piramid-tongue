"""Import vocabulary from Anki TSV export to Piramid-Tongue."""

import sqlite3
from pathlib import Path

# Anki TSV data - paste your exported content here
# Lines starting with # are metadata, skip them
ANKI_TSV = """#separator:tab
#html:true
#tags column:3
Bajo	Short	
De pie	Standing	
Viniendo	Coming	
Yendo	going	
Periódico	Newspaper	
Tener sed	To be thirsty	
Yo tampoco	Me Neither	
Frases	Sentences	
Escuchar	To listen to	
Corto	Short	
Empezar	To start	
Terminar	To finish	
Llevar (algo puesto)	To wear	
Chaqueta	Jacket	
Falda	Skirt	
Camiseta	T-Shirt	
Camisa	Shirt	
chompa, sueter, jersey	Sweater	
Pantalones cortos	Shorts	
Calcetines	Socks	
Traer	To bring	
Señalar	To point	
Nadar	To swim	
Llevar (transportar / portar)	To carry	
Montar	To ride	
Ver (la televisión)	To watch	
Revista	Magazine	
Irse, marcharse	To leave	
Quedarse	To stay	
Estar	To be	
Levantar (no me afecta y afecta al objeto o persn)	To raise (reiz)	
Subir (esta relacionado a que me incluye)	To rise (ráiz)	
Caerse	To fall, to drop	
Señalando a	Pointing at	
Encima de	On	
Allí	There	
Foto	Picture	
Sujetar	To hold	
lindo,precioso	Cute	
Oso	Bear	
Mascota	Pet	
detrás de	behind	
Supermercado	Grocery store	
Piso (de edificio)	apartment	
Dormitorio	Bedroom	
Baño	Bathroom	
Despertador	Alarm clock	
ruidoso	Loud	
Lámpara	Lamp	
cuadro	Painting	
Cine	Movie Theater	
Pelicula	Movie	
Divertido	Fun/Amusing	
Gracioso	Funny	
Hermanos (gral)	Siblings	
Hija	Daughter	
Mis hijos	My children	
Tía	Aunt	
Primo	Cousin	
Sobrino	Nephew	
Sobrina	Niece	
Paraguas	Umbrella	
Bolsa	Bag	
Bolso	Purse	
Monedero	Wallet	
Abrigo	Coat	
Bufanda	Scarf	
Sucio	Dirty	
Cerca de	Near (close)	
Lejos de	Far from	
Gasolinera	Gas station	
Panadería	Bakery	
Biblioteca	Library	
Librería	Bookstore	
Banco (para sentarse)	Bench	
Puente	Bridge	
Fuente	Fountain	
Lago	Lake	
Plaza	Square	
El centro	The center	
Girar	To turn	
Después	After	
Antes	Before	
Algunos, algo de, un poco de	Some	
¿Cuántos?	How many?	
¿Cuánto?	How much?	
Dinero	Money	
Bolsillo	Pocket	
Nevera	Refrigerator	
Vacío	Empty	
Lleno	Full	
Pan	Bread	
Verduras	Vegetables	
Zumo	Juice	
Jamón	Ham	
Mermelada	Jam	
Sopa	Soup	
Jabón	Soap	
Madera	Wood	
Horario	Schedule	
Apuntes	Notes	
Estuche	Pencil case	
Pinturas	Crayons	
Pintar	To color, to paint	
chicle	Gum	
Móvil	Cell phone	
Hablar por teléfono	To talk on the phone	
Ropa	Clothes	
Botas	Boots	
Invierno	Winter	
Primavera	Spring	
Verano	Summer	
Otoño	Fall	
Correcto	Right	
Incorrecto	Wrong	
Vivir	To live	
Cómodo	Comfortable	
Billete	Ticket	
Piedra	Rock	
Mosca	Fly	
Césped	Grass	
Cortar	To cut	
Tijeras	Scissors	
Gustar	To like	
Disfrutar	To enjoy	
Sentir	To feel	
Llenar	To fill	
Lavar	To wash	
Ojos	Eyes (ayz)	
Cuello	Neck	
Oreja	Ear	
Nada	Nothing	
Estar a salvo	To be safe	
Brazo	Arm	
Pierna	Leg	
Tobillo	Ankle	
Rodilla	Knee	
Roto	Broken	
Pie	Foot	
Pies	Feet	
Dedos de pie	Toes	
Medicina	Medicine	
Médico	Doctor	
Enfermera	Nurse	
Paciente	Patient	
Me duele	My Hurts	
Diente	 Tooth	
Dientes	Teeth	
Muletas	Crutches	
Por la mañana	In the morning	
Por la tarde	In the afternoon	
Por la noche	At night	
Los jueves	On Thursdays	
todos los días	Every day	
Todo el día	All day	
Una vez	Once	
Dos veces	Twice	
Despertarse	To wake up	
Despierto	Awake	
Listo	Ready	
Perfecto	Perfect	
Levantarse	To get up	
Vestirse	To get dressed	
Preparar	To prepare	
hacer (crear)	To make	
comida	Food	
Merienda	Snack	
El almuerzo	Lunch	
Almorzar	To have lunch	
Cenar	To have dinner	
La cena	Dinner	
Desayuno	Breakfast	
De quien	whose	
Salir (a la calle)	Go out	
Dentro	Inside	
Entra (desde adentro)	Come in	
Otra vez	Again	
Nubes	Clouds	
Nieve	Snow	
El viento	Wind	
Encontrar	To find	
Oír	To hear	
Pelo	Hair	
Rubio	Blonde	
Castaño	Brown, brunette	
Pelirrojo	Redhead	
Peine	Comb	
Peinarse	To brush, comb	
Cepillo de dientes	Toothbrush	
Ducha	Shower	
Ducharse	To take a shower	
Limpiar la casa	To clean the house	
Hacer la cama	To make the bed	
Lavar los platos	To wash the dishes	
Ir de compras	To go shopping	
comprar	To shop, buy	
Trabajador, obrero	Worker	
Empresa	Business, company, employer	
Trabajador	Hardworker	
Trabajo, empleo	Job, employment	
Fábrica	Factory	
Mecánico	Mechanic	
Ingeniero	Engineer	
Hombre, mujer de negocios	Businessman, business woman	
Fuerte	Strong	
Débil	Weak	
Inteligente	Smart	
Genial	Great	
Cuidadoso	Careful	
Parar	To stop	
Decidir	To decide	
Recordar	To remember	
Relajarse	To relax	
La mitad	Half	
Sobre, alrededor, acerca de	About	
ver	To see	
Mejorar	To improve	
Entender, comprender	To understand	
Practicar, entrenar	To practice	
Deportes	Sports	
Hacer deporte	To work out, To exercise	
Natación	Swimming	
Tenis Deportivos	Tennis shoes, running shoes	
Levantar (Hacer) pesas	To lift weights	
Jugador	Player	
Baloncesto	Basketball	
Beisbol	Baseball	
Rápido	Quick	
Rápidamente	Quickly	
Despacio	Slow	
Atrapar	To catch	
Lanzar	To throw	
Entrenador	Coach, trainer	
Aficionado	Fan	
Ganar	To win, to beat	
Perder	To lose, to miss	
Cuál?	Which?	
Preferir	To prefer	
Tipo, clase	Kind, type	
Pasar	To pass	
Carne	Meat	
Delicioso	Delicious	
Papas (comida)	Potatoes	
La barra, el bar	Bar	
Camarero (de mesas)	Waiter, waitress	
Pedir, ordenar	To order	
Sin (esp)	Without	
Solo, solamente	Only	
Pesado	Heavy	
Ligero	Light	
Utilizar	To use	
Plato	Plate	
Tenedor	Fork	
Subir	Go up	
Bajar (movimiento/descender)	Go down	
Escaleras	Stairs	
Escalones	Steps	
Abajo (piso de abajo)	Downstairs	
Arriba (piso)	Upstairs	
Oficina	Office	
Edificio	Building	
Reunión	Meeting	
Llegar	To get to, arrive	
Tarde (no llegar a tiempo)	Late	
Llegar tarde	To be late, To run late	
Llegar a tiempo	To be on time	
Llegar pronto	To be early	
Temprano	Early	
Depende de	It depends on	
Explicar	To explain	
Esperar	To wait, espect, hope	
Pantalla	Screen	
Por internet	Online	
Archivo	File	
Teclear	To type	
Marcar un número	To dial	
Especial	Special	
Fiesta	Party	
Huésped, invitado	Guest	
Invitar	To invite	
Cerveza	Beer	
Ruido	Noise	
Ruidoso	Noisy	
Globo	Balloon	
Fecha	Date	
Cartel	Poster	
Dolor de cabeza	Headache	
Alterado	Upset	
Bailar	To dance	
Juntos	Together	
Abarrotado	Crowded, packed	
Hacer una foto	To take a picture	
Sofá	Couch	
Balcón	Balcony	
Pasillo	Hallway	
Divertirse	To have fun (to have a good)	
Ponerse mal (enfermarse)	To get sick	
Celebrar	To celebrate	
Cada cuánto?	How often?	
Normalmente	Usually	
A veces	Sometimes	
A menudo	Often	
Casi nunca	Hardly ever	
La playa	The beach	
Maleta	Suitcase	
Hacer la maleta	To pack	
Viajar	To travel	
Volar	To fly	
Vuelo	Flight	
Deberes	Homework	
Fin de semana	Weekend	
Ir a correr	To go running	
Relajante	Relaxing	
Senderismo	Hiking	
Aeropuerto	Airport	
Vacaciones	Vacation	
Pagar	To pay	
Interesado en	Interested in	
Pasar tiempo	To spend time	
Tiempo libre	Free time	
Escalar	To climb	
Montañismo	Climbing	
Acampar	To camp	
El campo	The country	
Paisaje	Landspace	
Hacer turismo	Sightseeing	
Catedral	Cathedral	
Estadio	Stadium	
Concierto	Concert	
Barbacoa	Barbecue	
El mejor	The best	
Asombroso	Amazing	
Emocionante	Exiting	
Emocionado	Excited	
Peligroso	Dangerous	
Aventura	Adventure	
Aventurero	Adventurous	
Devolver, vómitar	To throw up	
devolver	To return, to take back	
Regalo	Gift, present	
Tamaño	Size	
Precio	Price	
Costar, valer	To cost	
Guardar, ahorrar	To save	
Pendientes (obj)	Earrings (object)	
Collar	Necklace	
Cinturón	Belt	
Ponerse	To put on	
Quitarse, despegar	To take off	
Quitarse/ despegar	To take off	
meter	To put in	
Sacar	To take out	
Gafas de sol	Sunglasses	
Carnet de conducir	drivers license	
Sandalias	sandals	
Policía	Policeman, policewoman	
Robar	To steal, to rob	
Seguir	To follow	
Al otro lado de	Across	
Tomar un taxi, bus, etc	To take, a taxi, bus etc	
Nadie	Nobody	
Todo el mundo	Everybody	
Cualquiera	Anybody	
De verdad?	Really?	
Por todas partes	Everywhere	
En ninguna parte	Nowhere	
Algún lugar	Somewhere	
Cualquier sitio	Anywhere	
Extraño	Strange, weird	
Poder (pasado de puedo)	To be able to	
Anuncio	Commercial	
Partido	Match, game	
Conversación	Conversation	
Una serie	A series	
Programa de television	Show	
Intentar	To try	
Esfuerzo	Effort	
Recibir	To get, receive	
Hacer caso	To listen to someone	
Probablemente	Probably	
Prestar atención a	To pay attention to	
En realidad	Actually	
Personalmente	Personally	
Probar	To taste, try	
Recomendar	To recommend	
Hielo	Ice	
Tostada	Toast	
Aceite de oliva	Olive oil	
Miel	Honey	
Ajo	Garlic	
Fresco	Fresh	
Champiñones	Mushrooms	
Pimiento	Pepper	
Pimienta	(Black) Pepper	
Frito	Fried	
Sano	Healthy	
Salud	Health	
Postre	Dessert (dihzirt)	
Desierto	Desert	
bajar	To lower	
Dulces	Candy	
Dulce	Sweet	
Galletas	Cookies	
Cuñada	Sister-in-law	
Yerno	Son-in-law	
Abuelo	Grandpa	
Abuela	Grandma	
Nieto	Grandson	
Nieta	Granddaughter	
Relación	Relationship	
Amistad	Friendship	
Amigable	Friendly	
Amable	Kind	
Barba	Beard	
Bigote	Mustache	
Desagradable	Unpleasant	
Tímido	Shy	
Guay	Cool	
Ocupado	Busy	
Vago	Lazy	
Atractivo	Attractive	
Guapo, atractivo	Good looking	
Educado	Polite	
Secretaria	Secretary	
Dentista	Dentist	
Fotógrafo	Photographer	
Tierra(terreno)	Land	
Bosque	Forest, woods	
Naturaleza	Nature	
Camino	Path	
Ancho	Wide	
Estrecho	Narrow	
Recto	Straight	
Afuera	Outside	
Auténtico, real	Actual, real	
Huerto, jardín	Garden	
Zanahoria	Carrot	
Jaula	Cage	
Cárcel	Jail	
Explotación agrícola	Farm	
Agricultor	Farmer	
Tractor	Tractor	
Colina	Hill	
Maíz	Corn	
Cereales	Cereal	
Pato	Duck	
Perrito	Puppy	
Caballo	Horse	
Vaca	Cow	
Conejo	Rabbit	
Gallo	Rooster	
Adolecente	Teenager	
Adulto	Adult	
Uniforme	Uniform	
Actor	Actor	
Actriz	Actress	
Presidente	President	
Piloto	Pilot, driver	
Ninguno	None	
nadie (variante)	No one, Nobody	
Todos	All	
todo el mundo (variante)	Everyone, everybody	
Ambos	Both	
La mayor parte	Most	
Generalmente	Generally	
Ganar (dinero)	To earn	
Imitar	To imitate	
Actuar	To act	
Imaginar	To Imagine	
Construir	To build	
Reparar	To repair	
Motor	Engine	
Helicóptero	Helicopter	
Cuando sea	Whenever	
Lo que sea	Whatever	
Música clásica	Classical music	
Cantante	Singer	
Escritor	Writer	
Ingenioso, inteligente(al humano)	Talented	
Popular	Popular	
Diferente, inusual	Unusual	
Conocido	Well-known	
Agradable (el disfrute)	Enjoyable	
Terrible	Terrible	
Canción	Song	
Sonido	Sound	
Instrumento	Instrument	
Micrófono	Microphone	
Voz	Voice	
Altavoz	Speaker	
Trompeta	Trumpet	
Saltar	To jump	
Gritar	To shout	
Ensayar	To practice (band)	
Bajar, descargar (internet)	To download	
Incluir	To include	
Comprobar	To check	
Correo	Mail	
Buzón	Mailbox	
Ir a casa	To go home	
Indicación, dirección	Direction	
Por supuesto	Of course	
Curso	Course	
Por cierto	By the way	
Descanso	Break	
Descansar	To rest	
Ve más deprisa	To pick up the pace	
Fotografía	Photography	
Un buen partido	A good catch	
Sugerir	To suggest	
En vez de	Instead, instead of	
Bien, vale, de acuerdo	Alright	
Imposible	Impossible	
Temperatura	Temperature	
Mojado	Wet	
Seco	Dry	
Nublado	Cloudy	
Neblinoso	Foggy	
Tormenta	Storm	
Trueno	Thunder	
Algún día	Someday	
Convencer	To convince	
Ocurrir	To happen	
Unir	To join	
Cultivar, crecer	To grow	
Propio	Own	
Pesca	Fishing	
Teatro	Theater (thíudur)	
Cita (entrevista)	Appointment	
Excusa	Excuse	
Lío, quilombo	Mess	
Puzzle	Puzzle	
Proyecto	Project	
Un cambio	A change	
Buscar, consultar	To look up	
Información	Information	
Actividades	Activities	
Dibujos animados	Cartoons	
Centrarse	To concentrate, to focus	
Estar aburrido	To be bored	
Ser aburrido	To be boring	
Mí, yo mismo	Myself	
Ti, tú mismo	Yourself	
Espejo	Mirror	
Casi	Almost	
Todavía	Still	
Olvidarse	To forget	
Repetirse	To repeat oneself	
Golpear	To hit	
Rascar	To scratch	
Picor	Itch	
Picar	To itch	
Sonar	To sound	
Sonidos	Sounds	
Sabor	Taste, flavor	
Saborear	To taste	
Buena jugada	Good move	
Parecer	To look like, to seem like	
Lo mismo	The same	
Estar seguro	To be sure	
Para siempre	For good	
Menos mal	It's a good thing	
quizás	Maybe	
Más o menos, un poco	Kind of	
¡Eso es!	You got it!	
Sonar (timbre, teléfono)	To ring	
Recoger, agarrar, contestar, levantar	To pick up, answer	
Elegir (variante)	To pick	
Pasar el rato (variante)	To hang around	
Matar el tiempo	To kill time	
Después, luego, entonces	Then	
Preocuparse	To worry	
Anoche	Last night	
"Echar de menos, perder (bus, evento)"	To miss	
Empezar (variante)	To begin, to start	
El comienzo	The beginning	
Principiante	Beginner	
Prometer	To promise	
Promesa	Promise	
Secreto	Secret	
Mantener, guardar	To keep	
Entre (variante de tipo rodeado)	Among	
Creer	To believe	
Es posible	It's possible	
Tan pronto como	As soon as	
Hasta	Until	
Recordar a alguien	To remind	
Acordarse	To remember	
Suspender	To fail	
Aprobar	To pass	
Examen	Test, exam	
Error	Mistake	
Con suerte	Hopefully	
reprobar, fallar, rajar, suspender	To flunk	
Comunicar, hacer saber	To let someone know	
Decisión	Decision	
Ponerse en contacto	To contact	
Compartir	To share	
Encender	To turn on	
Apagar	To turn off	
Interruptor de luz	Light switch	
Funcionar	To work (it works)	
Útil	Useful	
Ordenador portátil	Laptop	
Ordenador (de mesa)	Desktop computer	
Teclado	Keyboard	
Auriculares	Headphones	
Internet	Internet	
Conexión	Connection	
Comunicación	Communication	
Salón (casa)	Living room	
Ascensor	Elevator	
Alquilar	To rent	
El alquiler	The rent	
Vender	to sell	
Ofrecer	To offer	
Gratis	Free	
Disponible	Available	
De chiripa	By a fluke, a fluke	
Mudarse	To move (trasladar)	
Tejado	Roof	
Vista	View	
Muebles	Furniture	
Armario	Cupboard	
Hormiga	Ant	
Cucaracha	Cockroach	
Cuero	Leather	
Oscuro	Dark	
Duro	Hard	
Suave	Soft	
Excelente	Excellent	
Calidad	Quality	
Moqueta (que cubre el suelo)	Carpet	
Alfombra	Rug	
Director, gerente	Manager	
Ladrón	Thief	
Pelele	Pushover	
Investigar	To investigate	
Escapar	To escape	
Matar	To kill	
Empujar	To push	
Tirar	To pull	
Salida	Exit	
Entrada	Entrance	
Cerrar con llave	To lock	
Cerrado con llave	Locked	
Parada	Stop	
Únicamente	Only	
Sorprendido	Surprised	
Sorpresa	Surprise	
Desafortunadamente	Unfortunately	
Desafortunado	Unlucky	
Afortunadamente	Fortunately	
Afortunado	Lucky	
Perdido	Missing, lost	
Joyería	Jewelry shop	
Funda	Case	
Copia	Copy	
Ticket de compra	Receipt	
Deletrear	To spell	
Desarrollar	To develop	
Hacerse mayor, madurar	To grow up	
Soñar	To dream	
Soñar con	To dream about	
Pedir prestado	To borrow	
Prestar, dejar	To lend	
Dejar, irse	To leave	
Completar	To complete	
De cero	From scratch	
Pedir perdón	To apologize	
Perdonar	To forgive	
Comportarse	To behave	
Grabar	To record	
Darse prisa	To hurry	
Tener prisa	To be in a hurry	
Solo	Alone	
Quizás	Perhaps	
Posiblemente	Possibly	
Cuidadosamente	Carefully	
Fácilmente	Easily	
Al final	In the end	
Por fin, finalmente	Finally	
Jugársela, presionar	To push it	
Bastantes	Quite a lot, quite a few	
Bastante, suficiente	Enough	
Demasiado	Too much	
Demasiados	Too many	
Mentir	To lie	
Horrible	Horrible	
Sencillo	Simple	
Permitir, dejar	To allow, let	
Gastar dinero	To spend money	
Malgastar	To waste	
Electricidad	Electricity	
Batería (de auto)	Battery	
Espacio	Space	
Memoria	Memory	
Riesgo	Risk	
Opción	Option	
Elección	Choice	
Monedas	Coins	
Helado	Ice cream	
champaña	Champagne	
Cigarro	Cigarette	
Estar de acuerdo	To agree	
Estar de desacuerdo	To disagree	
Hablar (algo)	To discuss (something)	
Además de	As well as	
Parecido a	Similar to	
Diferente a	Different from	
Varios, diferentes	Various	
Creencias	Beliefs	
Clima	Climate	
Experiencia	Experience	
Básicamente	Basically	
Exactamente	Exactly	
Casi (variante almost)	Nearly	
Moderno	Modern	
Genial (asombroso)	Awesome	
Grande	Large	
Impresionante	Impressive	
Barrio	Neighborhood	
Vecino	Neighbor	
Plantar cara a	To stand up to	
Correos	Post office	
Garaje	Garage	
Parking	Parking lot	
Aparcar	To park	
Cruzar	To cross	
Volver (al sitio de inicio)	Get back	
estoy en ello, estoy dentro	I'm into it	
Montar	To ride	
Monopatín	Skateboard	
Cocinar al horno	To bake	
Mayonesa	Mayonnaise (maines)	
Mostaza	Mustard	
Hamburguesas	Hamburgers	
Tortilla	Omelet	
Pasta	Pasta	
Salsa	Sauce	
Tomar una decisión	To make a decision	
Instrucciones	Instructions	
Buscar (busqueda)	To search	
Publicar (en internet)	To post	
Crear	To create	
Apodo	Nickname	
Chatear, charlar, conversar	To chat	
Otro	Another	
Imprimir	To print	
Más	More	
Hoy en día	Nowadays	
Si no	Otherwise	
Indudablemente	Definitely	
Permitirse el lujo de	To afford	
Mejor	Better	
Peor (uso:comparativo)	Worse	
El peor	The worst	
Famoso	Famous/Celebrity	
Oro	Gold	
Plata	Silver	
Perfume	Perfume (perfíum)	
A no ser que	Unless	
Donar, repartir, retratarse, revelar	To give away	
De rebajas	On sale	
Descuento	Discount	
Viaje	Trip	
Transporte	Transportation	
Aerolínea	Airline	
Isla	Island	
En el extranjero	Abroad	
Equipaje	Luggage	
Asignatura	Subject	
Tema	Topic	
Estudios	Studies	
Ciencias	Science	
Científico	Scientist	
Geografía	Geography	
Química	Chemistry	
Física	Physics	
Biología	Biology	
Historia	History	
Cuento	Story	
El espacio	Space	
Sitio	Place	
Estrellas	Stars	
El cielo	Sky	
Planetas	Planets	
La tierra	Earth	
Compañeros de clase	Classmates	
Compañeros del trabajo	Workmates, colleagues	
Parientes	Relatives	
Gobierno	Government	
Economía	Economics	
La moda	Fashion	
Estar a la moda	To be fashionable	
Corbata	Tie	
Traje	Suit	
impermeable, gabardina	Raincoat	
Estar vestido	Dressed	
Común	Common	
contagiado, resfriado	Cold	
contagiarse (resfriarse)	To catch a cold	
Cuidar	To take care of	
Nacer	To be born	
Felicitar	To congratulate	
Enhorabuena (por)	Congratulations (on)	
Alegrarse de	To be glad	
Complacerse	To be pleased	
Emergencia	Emergency	
Estar malo	To be ill, sick	
Sangrar	To bleed	
Morir	To die	
Muerto	Dead	
Tener miedo	To be afraid	
Valiente	Brave	
Principalmente	Mainly	
Absolutamente	Absolutely, completely	
Planificar	To plan, arrange	
Asistir a un sitio	To attend somewhere	
Conocer (por primera vez)	To meet	
Quedar (con alguien)	To meet (with someone)	
De todas formas	Anyway	
Enorme	Huge, enormous	
Maravilloso	Wonderful	
Estresado	Stressed	
Estrés	Stress	
Agotado (emocional)	Exhausted	
Motivado	Motivated	
Entrevista	Interview	
Presión	Pressure	
Inventar (crear algo nuevo)	To invent	
Inventarse algo(excusa)	To make up	
Carrera	Race	
Concurso	Competition	
Meta (a la vez: gol)	Goal	
Premio	Prize	
Comparar	To compare	
Variedad	Variety	
Refresco	Soda pop	
Melón	Melon	
Fresas	Strawberries	
Lechuga	Lettuce	
Cordero	Lamb	
Vitaminas	Vitamins	
Dieta	Diet (dayhit)	
Especias	Spices	
Soso, blando, insípido	Bland	
Picante	Spicy	
Energía	Energy	
Activo	Active	
Mejora	Improvement	
Admirar	To admire	
Merecer	To deserve	
Contar	To count	
Contener	To contain	
Insistir en	To insist on	
Sin embargo, aunque	However	
Preguntarse (uno mismo)	To wonder	
Existir	To exist	
Molestar	To bother	
Significar, querer decir	To mean	
Importar	To matter	
Hacer trampa	To cheat	
Tratar con (acordar)	To deal with	
Rellenar, informar, sustituir	To fill in	
Varios	Several	
Entero	Whole	
Solicitar	To apply	
Solicitud	Application	
Firmar	To sign	
Firma	Signature	
Estar encargado	To be in charge of	
Un consejo	A piece of advice, a tip	
Aconsejar	To advise	
Creer en	To believe in	
Experto	Expert	
Destreza	Skill	
Responsable	Responsible	
Genio	Genius	
Único	Only, unique	
Embarazada	Pregnant	
Embarazoso	Embarrassing	
Espectáculo	Performance	
Entretenido	Entertaining/Amused	
Documental	Documentary	
Temporal	Temporary	
Aplaudir	To clap	
Serio	Serious	
De madera	Wooden	
Zoo	Zoo	
Salvaje, silvestre	Wild	
Vida salvaje	Wildlife	
Criatura	Creature	
Especies	Species	
Selva tropical	Rainforest	
El medio ambiente	The environment	
Selva, jungla	Jungle	
Recursos naturales	Natural resources	
Contaminación	Pollution	
Destruir	To destroy	
Reciclar	To recycle	
Ahorrar energía	To save (energy)	
Malgastar energía	To waste (energy)
"""


def parse_anki_tsv(tsv_content: str) -> list[tuple[str, str]]:
    """Parse Anki TSV export, returning list of (word, definition) tuples."""
    words = []
    for line in tsv_content.strip().split('\n'):
        line = line.strip()
        # Skip metadata lines
        if line.startswith('#'):
            continue
        # Split by tab
        parts = line.split('\t')
        if len(parts) >= 2:
            word = parts[0].strip()
            definition = parts[1].strip()
            # Skip if empty
            if word and definition:
                words.append((word, definition))
    return words


def import_vocab(db_path: str, words: list[tuple[str, str]]) -> int:
    """Import vocabulary into the database. Returns count of imported words."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    count = 0
    for word, definition in words:
        try:
            cursor.execute(
                """INSERT INTO vocab (word, definition, status) VALUES (?, ?, 'new')""",
                (word, definition)
            )
            count += 1
        except sqlite3.IntegrityError:
            # Word already exists, skip
            pass
    conn.commit()
    conn.close()
    return count


def main():
    db_path = Path(__file__).parent.parent / "data" / "progress.db"
    
    print("Parsing Anki TSV export...")
    words = parse_anki_tsv(ANKI_TSV)
    print(f"Found {len(words)} vocabulary entries")
    
    print(f"Importing to {db_path}...")
    count = import_vocab(str(db_path), words)
    print(f"Successfully imported {count} words!")


if __name__ == "__main__":
    main()
