"""Importa una sola vez el canon recibido, sin sustituir datos ni completar lagunas."""
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import app

SOURCE = Path(__file__).parent / 'canon' / 'fathia.md'
PARTIAL_KEY = 'fathia-documento-maestro-01-incompleto'
PREVIOUS_KEY = 'fathia-documento-maestro-02-completo'
IMPORT_KEY = 'fathia-documento-maestro-03-control-jugadores'
CONTROL_TITLE = 'Control de personajes · todos controlados por jugadores'
CHRONOLOGY_TITLE = 'Cronología general · fechas y orden parcial'
CHRONOLOGY_TITLES = [
    'El gremio mercenario', 'Horo desarrolla sentimientos', 'La declaración de Horo',
    'La misión en Fathia', 'El inquisidor guarda el secreto', 'La compra del caserón',
    'La formación de la familia', 'Hikari encuentra a Fumi', 'Fumi, Enzi y la colaboración con Eiko',
    'Salama encuentra a Fumi y vive cerca de Fathia', 'La relación de Enmy y Salama',
    'Víctor conoce a Lerey y comienzan las cartas', 'Víctor rescata a Pip',
    'IA crea a Mary y Mimy', 'Los proyectos del dojo y el restaurante',
    'Exusiai y Lappland trabajan para Samael',
]


def chronology_date(number):
    if number <= 6:
        return f'Secuencia confirmada · {number} · sin fecha exacta'
    return f'Orden relativo no confirmado · referencia documental {number} · sin fecha exacta'


def plain(text):
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.M)
    return text.replace('**', '').strip().removesuffix('---').strip()


def records():
    source = SOURCE.read_text(encoding='utf-8')
    split = re.split(r'^# (\d+)\. .*\n', source, flags=re.M)
    sections = {int(split[i]): split[i + 1].strip().removesuffix('---').strip()
                for i in range(1, len(split), 2)}
    secondary = re.split(r'^## (.+)\n', sections[15], flags=re.M)
    people = {secondary[i]: plain(secondary[i + 1]) for i in range(1, len(secondary), 2)}
    residents = ('Enzi', 'Horo', 'Shiey', 'Hikari', 'Fumi', 'Asuka', 'Yuna', 'Aria', 'IA', 'Pip', 'Mary', 'Mimy')
    characters = []
    for name, number in [('Enzi', 4), ('Horo', 5), ('Shiey', 6), ('Hikari', 7), ('Fumi', 8),
                         ('Asuka', 9), ('Yuna', 10), ('Aria', 11), ('IA', 12), ('Pip', 14)]:
        characters.append({'nombre': name, 'historia': plain(sections[number])})
    mary, mimy = sections[13].split('### Mary\n', 1)[1].split('### Mimy\n', 1)
    mimy = mimy.split('**Ambas viven', 1)[0]
    for name, appearance in [('Mary', mary), ('Mimy', mimy)]:
        characters.append({'nombre': name, 'historia': 'Sirvienta creada por IA para Horo. Vive permanentemente en el caserón; no es una visitante ocasional.\n\nApariencia\n\n' + plain(appearance)})
    for name in ('Salama', 'Eiko', 'Jazmín', 'Benienma-Sama', 'Lerey', 'Sery Factar'):
        characters.append({'nombre': name, 'historia': people[name.upper()]})
    for name in ('Exusiai', 'Lappland'):
        characters.append({'nombre': name, 'historia': plain(sections[16])})
    for character in characters:
        name = character['nombre']
        character['identidades'] = 'Víctor; Enmy' if name == 'Enzi' else ''
        character['control'] = 'Jugadores'
        character['residencia'] = 'Caserón de Enzi' if name in residents else (
            'Casita de hojas y ramas en un bosque cercano a Fathia' if name == 'Salama' else '')

    relations = []

    def link(a, b, kind, description, identity=''):
        relations.append({'origen': a, 'destino': b, 'tipo': kind, 'descripcion': description,
                          'identidad_origen': identity, 'identidad_destino': ''})

    link('Enzi', 'Horo', 'Pareja confirmada', 'Horo es la primera pareja de Enzi. Ella se declaró y le enseñó progresivamente el amor romántico. Después aceptó que amara a otras mujeres.')
    for name in ('Shiey', 'Hikari', 'Fumi', 'Asuka', 'Aria'):
        link('Enzi', name, 'Pareja confirmada', f'Enzi y {name} son pareja, según el canon confirmado.')
    link('Enzi', 'Yuna', 'Alumna · romance parcial', 'Enzi enseña artes marciales a Yuna. El vínculo romántico es parcial: no es un matrimonio ni una relación plenamente definida.')
    link('Enzi', 'Salama', 'Pareja confirmada bajo identidad Enmy', 'Enmy mantiene una relación amorosa con Salama. Salama cree que Enmy es la hermana de Enzi y no conoce la identidad compartida.', 'Enmy')
    link('Exusiai', 'Lappland', 'Pareja confirmada', 'Mantienen una relación amorosa y cariñosa; trabajan juntas en Samael.')
    link('Horo', 'Asuka', 'Familia', 'Horo y Asuka son hermanas.')
    link('Fumi', 'Eiko', 'Amistad · socias', 'Son amigas y socias en la confección de prendas. Eiko tiene una tienda de ropa en Fathia y no sabe que Fumi es un hada. No hay romance confirmado.')
    link('Lerey', 'Sery Factar', 'Amistad de infancia', 'Son amigas desde la infancia. Sery sabe que Lerey es una vampiresa; no es el inquisidor incidental de la antigua misión.')
    link('Aria', 'Benienma-Sama', 'Compañeras', 'Benienma-Sama ayudó a Aria a prepararse para ser una buena esposa. No se establece un romance entre ellas.')
    for name in ('Exusiai', 'Lappland'):
        for other in ('Enzi', 'Horo'):
            link(name, other, 'Antiguo gremio mercenario', 'Fueron compañeros del mismo gremio mercenario. Actualmente Exusiai y Lappland pertenecen a Samael; Enzi y Horo lo desconocen. Samael y el antiguo gremio son organizaciones distintas.')
    for name in ('Mary', 'Mimy'):
        link('IA', name, 'Creación', f'IA creó a {name} para ayudar a Horo. Ambas viven permanentemente en el caserón.')
        link(name, 'Horo', 'Servicio', f'{name} es una sirvienta creada por IA para ayudar a Horo.')
    link('IA', 'Horo', 'Ayuda', 'IA creó a Mary y Mimy para ayudar a Horo; es una sirvienta salomónica, no una pareja de Enzi.')
    link('Hikari', 'Fumi', 'Encuentro · acogida', 'Hikari fue la primera persona que Fumi encontró en el mundo humano; después la llevó al caserón.')
    link('Enzi', 'Pip', 'Rescate bajo identidad Víctor', 'Víctor retiró una flecha vinculada a una maldición y curó a Pip. Posteriormente, un picotazo accidental en sus labios la transformó en humana. Cada beso alterna su forma; Pip no se transforma voluntariamente.', 'Víctor')
    link('Enzi', 'Lerey', 'Correspondencia bajo identidad Víctor', 'Víctor conoció a Lerey en una ciudad vecina; mantienen comunicación mediante cartas. Lerey no sabe que Víctor es Enzi ni conoce sus otras identidades. No hay romance confirmado.', 'Víctor')
    link('Salama', 'Fumi', 'Compromiso pasado · sentimiento actual incierto', 'Estaban comprometidas en el mundo de las hadas. Fumi escapó para no casarse. Salama la buscó y Fumi la rechazó porque decidió permanecer con Enzi. Salama aún siente algo por Fumi, pero no se ha confirmado si es amor romántico.')
    link('Enzi', 'Fumi', 'Ayuda mágica', 'Enzi puede aumentar su tamaño hasta el de una persona humana, mantenerlo cuanto desee y revertirlo. También puede modificar su apariencia para ocultar su naturaleza.')

    world = [
        {'titulo': 'Fathia · Gaïa · Imperio de Abel', 'historia': plain(sections[1])},
        {'titulo': 'El caserón, sus 12 residentes y los proyectos familiares', 'historia': plain(sections[2])},
        {'titulo': 'El antiguo gremio y la llegada de Enzi y Horo', 'historia': plain(sections[3])},
        {'titulo': 'Samael · organización clandestina', 'historia': plain(sections[17])},
        {'titulo': 'Tienda de ropa de Eiko', 'historia': 'Tienda de ropa en Fathia, propiedad de Eiko. Eiko y Fumi son socias y confeccionan prendas. Eiko desconoce que Fumi es un hada. La amistad y colaboración profesional no constituyen un romance confirmado.'},
        {'titulo': 'Bosque cercano a Fathia · hogar de Salama', 'historia': 'Salama vive en una casita que construyó con hojas, ramas y materiales naturales. No es una residente del caserón.'},
        {'titulo': 'Hotel de Benienma-Sama', 'historia': 'Hotel destinado a yokai en un mundo paralelo. Su propietaria, Benienma-Sama, puede visitar Gaïa. No se ha confirmado un nombre propio para el hotel.'},
        {'titulo': 'Imperium · procedencia de Aria', 'historia': 'Aria procede de Imperium. No hay más detalles de esta procedencia en el documento recibido.'},
        {'titulo': 'Mundo de las hadas', 'historia': 'Fumi y Salama proceden del mundo de las hadas. Allí estaban comprometidas. Fumi escapó al mundo humano porque no deseaba casarse con Salama.'},
        {'titulo': 'Reglas de continuidad del canon', 'historia': plain(split[0])},
        {'titulo': CHRONOLOGY_TITLE, 'historia': plain(sections[20])},
    ]
    for number, title in [
        (21, CONTROL_TITLE),
        (22, 'Tono de Fathia y vida cotidiana'),
        (23, 'Reglas visuales y prioridad de las imágenes originales'),
        (24, 'Proyectos y antecedentes creativos · no equivalen a hechos de la partida'),
        (25, 'Información no definida · consultar antes de confirmar'),
        (26, 'Reglas finales de continuidad'),
    ]:
        content = plain(sections[number])
        if number == 21:
            content += '\n\nACLARACIÓN POSTERIOR QUE PREVALECE\n\n' + plain(sections[27])
        world.append({'titulo': title, 'historia': content})
    secrets = []
    entries = re.split(r'\*\*Secreto (\d+): (.+?)\*\*', sections[19])
    for i in range(1, len(entries), 3):
        secrets.append({'titulo': f'Secreto {entries[i]}: {entries[i + 1]}', 'historia': plain(entries[i + 2])})
    chronology = re.findall(r'^(\d+)\. (.+)$', sections[20], flags=re.M)
    events = [{'titulo': CHRONOLOGY_TITLES[int(n) - 1], 'fecha': chronology_date(int(n)), 'historia': body}
              for n, body in chronology]
    events.append({'titulo': 'Asuka y Enzi · el té en el jardín', 'fecha': 'Escena registrada · fuera de la cronología confirmada',
                   'historia': plain(sections[9].split('### Escena registrada\n', 1)[1])})
    return {'personajes': characters, 'relaciones': relations, 'mundo': world, 'secretos': secrets, 'eventos': events}


def insert_record(db, table, record):
    fields = app.FIELDS[table]
    db.execute(f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({', '.join('?' for _ in fields)})",
               tuple(record[k] for k in fields))


def add_continuation(db, data):
    """Upgrade only the known partial import; protect later user edits."""
    initial = SOURCE.with_name('fathia-parte-inicial.md').read_text(encoding='utf-8')
    initial_chronology = initial.split('# 20. CRONOLOGÍA GENERAL CONFIRMADA\n', 1)[1]
    old_note = plain(initial_chronology) + ('\n\nNota de archivo: el mensaje recibido termina literalmente en '
               '«8. Hikari encontró a Fumi d». El punto 8 está incompleto; no se ha completado ni se han inferido acontecimientos posteriores.')
    new_note = next(r for r in data['mundo'] if r['titulo'] == CHRONOLOGY_TITLE)
    changed = db.execute('UPDATE mundo SET titulo = ?, historia = ? WHERE titulo = ? AND historia = ?',
                        (new_note['titulo'], new_note['historia'], 'Cronología recibida · continuación pendiente', old_note))
    if not changed.rowcount:
        # An edited or deleted note is retained as the user left it; add the new source separately.
        insert_record(db, 'mundo', new_note)
    for note in data['mundo'][11:]:
        insert_record(db, 'mundo', note)
    for number, event in enumerate(data['eventos'][:7], start=1):
        db.execute('UPDATE eventos SET fecha = ? WHERE titulo = ? AND fecha = ? AND historia = ?',
                   (event['fecha'], event['titulo'], f'Secuencia confirmada · {number}/7 · sin fecha exacta', event['historia']))
    for event in data['eventos'][7:16]:
        insert_record(db, 'eventos', event)
    scene = data['eventos'][16]
    db.execute('UPDATE eventos SET fecha = ? WHERE titulo = ? AND fecha = ? AND historia = ?',
               (scene['fecha'], scene['titulo'], 'Fecha y posición cronológica no confirmadas', scene['historia']))


def import_canon():
    data = records()
    db = app.connect()
    try:
        if db.execute('SELECT 1 FROM importaciones WHERE clave = ?', (IMPORT_KEY,)).fetchone():
            print('Canon ya incorporado. No se duplicaron ni sobrescribieron entradas.')
            return False
        complete = bool(db.execute('SELECT 1 FROM importaciones WHERE clave = ?', (PREVIOUS_KEY,)).fetchone())
        partial = bool(db.execute('SELECT 1 FROM importaciones WHERE clave = ?', (PARTIAL_KEY,)).fetchone())
        updating = complete or partial
        if not updating:
            # Name collisions require an explicit merge, never a silent overwrite.
            for person in data['personajes']:
                if db.execute('SELECT 1 FROM personajes WHERE lower(nombre) = lower(?)', (person['nombre'],)).fetchone():
                    raise ValueError(f"Ya existe {person['nombre']}. Revisa la integración antes de importar; no se cambió contenido.")
        backup_path = app.DB.parent / 'respaldos' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f') + '-antes-fathia.sqlite3')
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(backup_path) as backup:
            db.backup(backup)
        with db:
            if updating:
                if not complete:
                    add_continuation(db, data)
                else:
                    new_control = next(note for note in data['mundo'] if note['titulo'] == CONTROL_TITLE)
                    old_control = new_control['historia'].split('\n\nACLARACIÓN POSTERIOR QUE PREVALECE', 1)[0]
                    old_control += ('\n\nNota de archivo: en la continuación recibida no aparecen separadores que permitan '
                                    'asignar inequívocamente cada nombre a jugadores o secundarios. Clasificación pendiente '
                                    'de aclaración del usuario; no se asigna el control de ningún personaje por inferencia.')
                    changed = db.execute('UPDATE mundo SET titulo = ?, historia = ? WHERE titulo = ? AND historia = ?',
                                         (new_control['titulo'], new_control['historia'], 'Control de personajes · clasificación por aclarar', old_control))
                    if not changed.rowcount:
                        insert_record(db, 'mundo', new_control)
                for character in data['personajes']:
                    db.execute('UPDATE personajes SET control = ? WHERE nombre = ?', ('Jugadores', character['nombre']))
            else:
                ids = {}
                for person in data['personajes']:
                    insert_record(db, 'personajes', person)
                    ids[person['nombre']] = db.execute('SELECT last_insert_rowid()').fetchone()[0]
                for relation in data['relaciones']:
                    values = {**relation, 'origen': ids[relation['origen']], 'destino': ids[relation['destino']]}
                    insert_record(db, 'relaciones', values)
                for table in ('mundo', 'secretos', 'eventos'):
                    for record in data[table]:
                        insert_record(db, table, record)
            db.execute('INSERT INTO importaciones (clave) VALUES (?)', (IMPORT_KEY,))
        print('Canon incorporado: ' + ', '.join(f'{len(rows)} {table}' for table, rows in data.items()) + '.')
        print(f'Respaldo previo: {backup_path}')
        return True
    finally:
        db.close()


if __name__ == '__main__':
    import_canon()
