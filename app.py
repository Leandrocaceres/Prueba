"""Archivo de campaña: Python 3.10+, sin dependencias externas."""
import argparse
import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

DB = Path(os.environ.get('ROL_DB', Path(__file__).parent / 'datos' / 'campana.sqlite3'))
IMAGES = Path(__file__).parent / 'imagenes'
IMAGE_TYPES = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}
FIELDS = {
    'personajes': ('nombre', 'historia', 'identidades', 'residencia', 'control'),
    'relaciones': ('origen', 'destino', 'descripcion', 'tipo', 'identidad_origen', 'identidad_destino'),
    'eventos': ('titulo', 'fecha', 'historia'),
    'mundo': ('titulo', 'historia'),
    'secretos': ('titulo', 'historia'),
}


def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS personajes (
        id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, historia TEXT NOT NULL DEFAULT '');
    CREATE TABLE IF NOT EXISTS relaciones (
        id INTEGER PRIMARY KEY, origen INTEGER NOT NULL REFERENCES personajes(id) ON DELETE CASCADE,
        destino INTEGER NOT NULL REFERENCES personajes(id) ON DELETE CASCADE,
        descripcion TEXT NOT NULL, CHECK(origen != destino));
    CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY, titulo TEXT NOT NULL, fecha TEXT NOT NULL DEFAULT '',
        historia TEXT NOT NULL DEFAULT '');
    CREATE TABLE IF NOT EXISTS mundo (
        id INTEGER PRIMARY KEY, titulo TEXT NOT NULL, historia TEXT NOT NULL DEFAULT '');
    CREATE TABLE IF NOT EXISTS secretos (
        id INTEGER PRIMARY KEY, titulo TEXT NOT NULL, historia TEXT NOT NULL DEFAULT '');
    CREATE TABLE IF NOT EXISTS importaciones (
        clave TEXT PRIMARY KEY, fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    ''')
    # Additive migration: preserve campaigns created with the first version.
    for table, columns in {
        'personajes': ('identidades', 'residencia', 'control'),
        'relaciones': ('tipo', 'identidad_origen', 'identidad_destino'),
    }.items():
        existing = {row['name'] for row in db.execute(f'PRAGMA table_info({table})')}
        for column in columns:
            if column not in existing:
                db.execute(f"ALTER TABLE {table} ADD COLUMN {column} TEXT NOT NULL DEFAULT ''")
    db.commit()
    return db


def snapshot():
    with connect() as db:
        data = {table: [dict(row) for row in db.execute(f'SELECT * FROM {table} ORDER BY id')]
                for table in FIELDS}
    catalog = json.loads((IMAGES / 'referencias.json').read_text(encoding='utf-8'))
    for table, title in (('personajes', 'nombre'), ('mundo', 'titulo')):
        for entry in data[table]:
            reference = catalog.get(table, {}).get(entry[title], {})
            path = image_path(reference.get('archivo'))
            if path:
                entry['imagen'] = '/imagenes/' + path.name
                entry['imagen_alt'] = reference.get('alt') or entry[title]
            elif reference:
                entry['imagen_pendiente'] = True
            if table == 'personajes' and entry.get('identidades'):
                aliases = [name.strip() for name in entry['identidades'].split(';') if name.strip()]
                identities = reference.get('identidades', {})
                entry['formas'] = []
                for name in dict.fromkeys([entry['nombre'], *aliases]):
                    image = reference if name == entry['nombre'] else identities.get(name, {})
                    path = image_path(image.get('archivo'))
                    form = {'nombre': name}
                    if path:
                        form['imagen'] = '/imagenes/' + path.name
                        form['imagen_alt'] = image.get('alt') or f'Retrato de {name}'
                    else:
                        form['imagen_pendiente'] = True
                    entry['formas'].append(form)
    return data


def image_path(filename):
    """Only serve original image files directly inside the image directory."""
    if not isinstance(filename, str) or not filename or Path(filename).name != filename:
        return None
    candidate = (IMAGES / filename).resolve()
    if candidate.parent != IMAGES.resolve() or candidate.suffix.lower() not in IMAGE_TYPES:
        return None
    return candidate if candidate.is_file() else None


class Handler(BaseHTTPRequestHandler):
    def send(self, status, data, content_type='application/json; charset=utf-8'):
        body = data if isinstance(data, bytes) else (data.encode() if isinstance(data, str) else json.dumps(data, ensure_ascii=False).encode())
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = unquote(urlsplit(self.path).path)
        if route.startswith('/imagenes/'):
            path = image_path(route.removeprefix('/imagenes/'))
            if path:
                self.send(200, path.read_bytes(), IMAGE_TYPES[path.suffix.lower()])
            else:
                self.send(404, {'error': 'Imagen no disponible'})
        elif self.path == '/':
            self.send(200, Path(__file__).with_name('index.html').read_text(), 'text/html; charset=utf-8')
        elif self.path == '/api':
            self.send(200, snapshot())
        elif self.path == '/exportar':
            self.send(200, snapshot())
        elif self.path == '/canon':
            self.send(200, Path(__file__).with_name('canon').joinpath('fathia.md').read_text(encoding='utf-8'),
                      'text/plain; charset=utf-8')
        else:
            self.send(404, {'error': 'Página inexistente'})

    def do_POST(self):
        # A custom header prevents cross-site form submissions against the local app.
        if self.headers.get('X-Campana') != '1':
            return self.send(403, {'error': 'Solicitud no permitida'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 1_000_000:
                raise ValueError('Tamaño de solicitud inválido')
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError('Se requiere un objeto JSON')
            table = self.path.removeprefix('/api/')
            if table not in FIELDS:
                return self.send(404, {'error': 'Sección inexistente'})
            with connect() as db:
                if data.get('eliminar'):
                    db.execute(f'DELETE FROM {table} WHERE id = ?', (int(data['id']),))
                else:
                    values = []
                    current = None
                    if data.get('id'):
                        current = db.execute(f'SELECT * FROM {table} WHERE id = ?', (int(data['id']),)).fetchone()
                        if current is None:
                            return self.send(404, {'error': 'Entrada inexistente'})
                    for field in FIELDS[table]:
                        value = data.get(field, current[field] if current else '')
                        if field in ('origen', 'destino'):
                            value = int(value)
                        elif not isinstance(value, str):
                            raise ValueError('Texto inválido')
                        else:
                            value = value.strip()
                        if field in ('nombre', 'titulo', 'descripcion') and not value:
                            raise ValueError('Completa los campos obligatorios')
                        values.append(value)
                    if data.get('id'):
                        assignments = ', '.join(f'{f} = ?' for f in FIELDS[table])
                        db.execute(f'UPDATE {table} SET {assignments} WHERE id = ?', (*values, int(data['id'])))
                    else:
                        columns = ', '.join(FIELDS[table])
                        placeholders = ', '.join('?' for _ in values)
                        db.execute(f'INSERT INTO {table} ({columns}) VALUES ({placeholders})', values)
            self.send(200, snapshot())
        except (ValueError, TypeError, KeyError, sqlite3.IntegrityError):
            self.send(400, {'error': 'Revisa los campos obligatorios. Las relaciones necesitan dos personajes distintos y existentes.'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    with connect():
        pass
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Archivo de campaña iniciado en el puerto {args.port}. Ctrl+C para salir.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
