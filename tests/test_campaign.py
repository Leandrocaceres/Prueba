import base64
import contextlib
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

import app
import importar_fathia


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_db = app.DB
        app.DB = Path(self.temp.name) / 'campana.sqlite3'
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(setattr, app, 'DB', self.old_db)

    def seed(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return importar_fathia.import_canon()

    def test_canon_people_identities_and_residents(self):
        self.seed()
        people = app.snapshot()['personajes']
        self.assertEqual(len(people), 20)
        self.assertEqual(sum(p['residencia'] == 'Caserón de Enzi' for p in people), 12)
        names = {p['nombre']: p for p in people}
        self.assertNotIn('Víctor', names)
        self.assertNotIn('Enmy', names)
        self.assertEqual(names['Enzi']['identidades'], 'Víctor; Enmy')
        self.assertTrue(all(p['control'] == 'Jugadores' for p in people))
        self.assertIn('exactamente tres colas', names['Enzi']['historia'])
        self.assertIn('Yuna no tiene orejas ni cola verdaderas', names['Yuna']['historia'])
        self.assertIn('Horo no fue criada por la Iglesia', names['Horo']['historia'])
        self.assertIn('No habla cuando está en forma de ave', names['Pip']['historia'])
        self.assertIn('No puede controlar las transformaciones libremente', names['Pip']['historia'])
        self.assertNotIn('Cabello rosa', names['Mary']['historia'])
        self.assertNotIn('Cabello negro', names['Mimy']['historia'])

    def test_relationship_boundaries_and_secrets(self):
        self.seed()
        data = app.snapshot()
        people = {p['nombre']: p['id'] for p in data['personajes']}
        relations = data['relaciones']
        def between(a, b):
            return [r for r in relations if r['origen'] == people[a] and r['destino'] == people[b]]
        canonical_partners = [r for r in relations if r['origen'] == people['Enzi'] and r['tipo'] == 'Pareja confirmada']
        self.assertEqual(len(canonical_partners), 6)
        self.assertIn('parcial', between('Enzi', 'Yuna')[0]['tipo'])
        self.assertEqual(between('Enzi', 'Salama')[0]['identidad_origen'], 'Enmy')
        self.assertIn('cree que Enmy es la hermana', between('Enzi', 'Salama')[0]['descripcion'])
        self.assertEqual(between('Enzi', 'Lerey')[0]['identidad_origen'], 'Víctor')
        self.assertIn('Amistad', between('Fumi', 'Eiko')[0]['tipo'])
        self.assertIn('incierto', between('Salama', 'Fumi')[0]['tipo'])
        self.assertEqual(len(data['secretos']), 6)
        content = '\n'.join(s['historia'] for s in data['secretos'])
        for text in ['Eiko no sabe', 'Salama no sabe', 'Lerey desconoce', 'sin que Enzi y Horo conozcan']:
            self.assertIn(text, content)

    def test_full_chronology_preserves_partial_order_and_creative_limits(self):
        self.seed()
        data = app.snapshot()
        sequence = [e for e in data['eventos'] if e['fecha'].startswith('Secuencia confirmada')]
        unordered = [e for e in data['eventos'] if e['fecha'].startswith('Orden relativo no confirmado')]
        self.assertEqual(len(sequence), 6)
        self.assertEqual(len(unordered), 10)
        self.assertTrue(all('sin fecha exacta' in e['fecha'] for e in sequence + unordered))
        asuka = next(e for e in data['eventos'] if e['titulo'].startswith('Asuka'))
        self.assertIn('fuera de la cronología confirmada', asuka['fecha'])
        note = next(n for n in data['mundo'] if n['titulo'] == importar_fathia.CHRONOLOGY_TITLE)
        self.assertIn('8. Hikari encontró a Fumi después', note['historia'])
        self.assertIn('no significa necesariamente', note['historia'])
        source = importar_fathia.SOURCE.read_text()
        self.assertTrue(source.rstrip().endswith('FIN DEL DOCUMENTO MAESTRO DE FATHIA.'))
        world = '\n'.join(n['historia'] for n in data['mundo'])
        for text in ['Entre flores y escarcha', 'Discord y Gemini', 'no debe inventarse', 'todos son controlados por jugadores']:
            self.assertIn(text, world)
        self.assertFalse(any('continuación pendiente' in n['titulo'] for n in data['mundo']))

    def test_upgrade_partial_import_retains_edits_and_does_not_duplicate(self):
        # Fixture representing the previously imported, truncated document.
        self.seed()
        with app.connect() as db:
            db.execute('DELETE FROM importaciones')
            db.execute('INSERT INTO importaciones (clave) VALUES (?)', (importar_fathia.PARTIAL_KEY,))
            db.execute('DELETE FROM mundo WHERE id > 11')
            db.execute('DELETE FROM eventos WHERE id BETWEEN 8 AND 16')
            initial = importar_fathia.SOURCE.with_name('fathia-parte-inicial.md').read_text()
            old_history = importar_fathia.plain(initial.split('# 20. CRONOLOGÍA GENERAL CONFIRMADA\n', 1)[1])
            old_history += ('\n\nNota de archivo: el mensaje recibido termina literalmente en '
                            '«8. Hikari encontró a Fumi d». El punto 8 está incompleto; no se ha completado ni se han inferido acontecimientos posteriores.')
            db.execute('UPDATE mundo SET titulo = ?, historia = ? WHERE id = 11',
                       ('Cronología recibida · continuación pendiente', old_history))
            for n in range(1, 8):
                db.execute('UPDATE eventos SET fecha = ? WHERE id = ?', (f'Secuencia confirmada · {n}/7 · sin fecha exacta', n))
            db.execute("UPDATE eventos SET fecha = 'Fecha y posición cronológica no confirmadas' WHERE id = 17")
            db.execute("UPDATE personajes SET historia = 'Corrección del usuario' WHERE nombre = 'Horo'")
        self.assertTrue(self.seed())
        data = app.snapshot()
        self.assertEqual(len(data['personajes']), 20)
        self.assertEqual(len(data['relaciones']), 27)
        self.assertEqual(len(data['mundo']), 17)
        self.assertEqual(len(data['eventos']), 17)
        self.assertEqual(next(p for p in data['personajes'] if p['nombre'] == 'Horo')['historia'], 'Corrección del usuario')
        self.assertFalse(any('continuación pendiente' in n['titulo'] for n in data['mundo']))
        self.assertFalse(self.seed())
        self.assertEqual(app.snapshot(), data)

    def test_reimport_preserves_edits_and_deletions(self):
        self.assertTrue(self.seed())
        with app.connect() as db:
            db.execute("UPDATE personajes SET historia = 'Corrección del director' WHERE nombre = 'Horo'")
            db.execute("DELETE FROM personajes WHERE nombre = 'Jazmín'")
        before = app.snapshot()
        self.assertFalse(self.seed())
        self.assertEqual(app.snapshot(), before)
        self.assertEqual(len(list((app.DB.parent / 'respaldos').glob('*.sqlite3'))), 1)

    def test_existing_name_collision_does_not_overwrite_user_data(self):
        with app.connect() as db:
            db.execute("INSERT INTO personajes (nombre, historia) VALUES ('Enzi', 'Mi anotación previa')")
        before = app.snapshot()
        with self.assertRaisesRegex(ValueError, 'Ya existe Enzi'):
            self.seed()
        self.assertEqual(app.snapshot(), before)

    def test_migration_and_backup_preserve_existing_campaign(self):
        with sqlite3.connect(app.DB) as db:
            db.execute('CREATE TABLE personajes (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, historia TEXT NOT NULL DEFAULT "")')
            db.execute("INSERT INTO personajes VALUES (44, 'Personaje propio', 'Historia previa')")
        self.seed()
        own = next(p for p in app.snapshot()['personajes'] if p['id'] == 44)
        self.assertEqual(own['historia'], 'Historia previa')
        self.assertEqual(own['identidades'], '')
        backup = next((app.DB.parent / 'respaldos').glob('*.sqlite3'))
        with sqlite3.connect(backup) as db:
            self.assertEqual(db.execute('SELECT nombre, historia FROM personajes').fetchall(), [('Personaje propio', 'Historia previa')])

    def test_identity_portraits_belong_to_one_character(self):
        self.seed()
        directory = Path(self.temp.name) / 'formas'
        directory.mkdir()
        original_images = app.IMAGES
        app.IMAGES = directory
        self.addCleanup(setattr, app, 'IMAGES', original_images)
        image = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')
        for name in ('enzi-prueba.png', 'enmy-prueba.png'):
            (directory/name).write_bytes(image)
        catalog = {'personajes': {'Enzi': {'archivo': 'enzi-prueba.png', 'identidades': {
            'Enmy': {'archivo': 'enmy-prueba.png', 'alt': 'Imagen de prueba de una identidad'},
            'Víctor': {'archivo': None},
        }}}, 'mundo': {}}
        (directory/'referencias.json').write_text(json.dumps(catalog))
        state = app.snapshot()
        self.assertEqual(len(state['personajes']), 20)
        enzi = next(p for p in state['personajes'] if p['nombre'] == 'Enzi')
        self.assertEqual([form['nombre'] for form in enzi['formas']], ['Enzi', 'Víctor', 'Enmy'])
        forms = {form['nombre']: form for form in enzi['formas']}
        self.assertEqual(forms['Enzi']['imagen'], '/imagenes/enzi-prueba.png')
        self.assertEqual(forms['Enmy']['imagen'], '/imagenes/enmy-prueba.png')
        self.assertTrue(forms['Víctor']['imagen_pendiente'])
        self.assertNotIn('imagen', forms['Víctor'])
        self.assertFalse(any(p['nombre'] in ('Enmy', 'Víctor') for p in state['personajes']))

    def test_original_portrait_is_served_only_for_its_character(self):
        self.seed()
        image_dir = Path(self.temp.name) / 'imagenes'
        image_dir.mkdir()
        old_images = app.IMAGES
        app.IMAGES = image_dir
        self.addCleanup(setattr, app, 'IMAGES', old_images)
        original = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')
        (image_dir / 'fumi.png').write_bytes(original)
        catalog = {'personajes': {'Fumi': {'archivo': 'fumi.png', 'alt': 'Referencia de Fumi'}}, 'mundo': {}}
        (image_dir / 'referencias.json').write_text(json.dumps(catalog))
        data = app.snapshot()
        with_image = [p for p in data['personajes'] if p.get('imagen')]
        self.assertEqual([p['nombre'] for p in with_image], ['Fumi'])
        self.assertEqual(with_image[0]['imagen'], '/imagenes/fumi.png')
        self.assertIsNone(app.image_path('../campana.sqlite3'))
        (image_dir / 'enlace.png').symlink_to(app.DB)
        self.assertIsNone(app.image_path('enlace.png'))
        server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            root = f'http://127.0.0.1:{server.server_port}'
            with urllib.request.urlopen(root+'/imagenes/fumi.png') as response:
                self.assertEqual(response.headers['Content-Type'], 'image/png')
                self.assertEqual(response.read(), original)
            for path in ['/imagenes/%2e%2e/campana.sqlite3', '/imagenes/enlace.png', '/imagenes/referencias.json']:
                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(root+path)
                self.assertEqual(error.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()
            worker.join()
        (image_dir / 'fumi.png').unlink()
        data = app.snapshot()
        fumi = next(p for p in data['personajes'] if p['nombre'] == 'Fumi')
        self.assertTrue(fumi['imagen_pendiente'])
        self.assertNotIn('imagen', fumi)

    def test_http_edit_export_validation_and_restart(self):
        self.seed()
        def start():
            server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            return server, worker
        def stop(server, worker):
            server.shutdown()
            server.server_close()
            worker.join()
        server, worker = start()
        def request(path='/api', body=None, headers=None):
            payload = json.dumps(body).encode() if body is not None else None
            req = urllib.request.Request(f'http://127.0.0.1:{server.server_port}{path}', data=payload,
                                         headers=headers or {'Content-Type': 'application/json', 'X-Campana': '1'})
            with urllib.request.urlopen(req) as response:
                return response.read().decode()
        try:
            self.assertIn('Mundo y canon', request('/'))
            self.assertEqual(request('/canon'), importar_fathia.SOURCE.read_text())
            people = json.loads(request())['personajes']
            enzi = next(p for p in people if p['nombre'] == 'Enzi')
            request('/api/personajes', {'id': enzi['id'], 'historia': 'Corrección posterior'})
            exported = json.loads(request('/exportar'))
            edited = next(p for p in exported['personajes'] if p['id'] == enzi['id'])
            self.assertEqual(edited['identidades'], 'Víctor; Enmy')
            self.assertEqual(edited['residencia'], 'Caserón de Enzi')
            self.assertEqual(edited['historia'], 'Corrección posterior')
            for body in [[], {'origen': enzi['id'], 'destino': enzi['id'], 'descripcion': 'Inválida'}]:
                with self.assertRaises(urllib.error.HTTPError) as error:
                    request('/api/relaciones', body)
                self.assertEqual(error.exception.code, 400)
            with self.assertRaises(urllib.error.HTTPError) as error:
                request('/api/mundo', {'titulo': 'No autorizado'}, {'Content-Type': 'application/json'})
            self.assertEqual(error.exception.code, 403)
            for table in ('mundo', 'secretos'):
                result = json.loads(request('/api/'+table, {'titulo': 'Nueva nota', 'historia': '<script>texto literal</script>'}))
                note = result[table][-1]
                result = json.loads(request('/api/'+table, {'id': note['id'], 'historia': 'Nota corregida'}))
                self.assertEqual(result[table][-1]['titulo'], 'Nueva nota')
                request('/api/'+table, {'id': note['id'], 'eliminar': True})
        finally:
            stop(server, worker)
        server, worker = start()
        try:
            persisted = json.loads(request())
            self.assertEqual(next(p for p in persisted['personajes'] if p['nombre'] == 'Enzi')['historia'], 'Corrección posterior')
        finally:
            stop(server, worker)


if __name__ == '__main__':
    unittest.main()
