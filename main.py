from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Libro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    autor = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50), default='disponible')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/libros', methods=['GET'])
def get_libros():
    libros = Libro.query.all()
    return jsonify([{
        'id': l.id,
        'titulo': l.titulo,
        'autor': l.autor,
        'isbn': l.isbn,
        'categoria': l.categoria,
        'estado': l.estado,
        'fecha_creacion': l.fecha_creacion.isoformat()
    } for l in libros])

@app.route('/libros/<int:id>', methods=['GET'])
def get_libro(id):
    libro = Libro.query.get_or_404(id)
    return jsonify({
        'id': libro.id,
        'titulo': libro.titulo,
        'autor': libro.autor,
        'isbn': libro.isbn,
        'categoria': libro.categoria,
        'estado': libro.estado,
        'fecha_creacion': libro.fecha_creacion.isoformat()
    })

@app.route('/libros', methods=['POST'])
def create_libro():
    data = request.get_json()
    if not data or not all(k in data for k in ('titulo', 'autor', 'isbn', 'categoria')):
        return jsonify({'error': 'Faltan datos requeridos'}), 400

    if Libro.query.filter_by(isbn=data['isbn']).first():
        return jsonify({'error': 'El ISBN ya existe'}), 400

    libro = Libro(
        titulo=data['titulo'],
        autor=data['autor'],
        isbn=data['isbn'],
        categoria=data['categoria'],
        estado=data.get('estado', 'disponible')
    )
    db.session.add(libro)
    db.session.commit()
    return jsonify({'message': 'Libro creado exitosamente', 'id': libro.id}), 201

@app.route('/libros/<int:id>', methods=['PUT'])
def update_libro(id):
    libro = Libro.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    if 'titulo' in data:
        libro.titulo = data['titulo']
    if 'autor' in data:
        libro.autor = data['autor']
    if 'isbn' in data:
        if Libro.query.filter_by(isbn=data['isbn']).first() and libro.isbn != data['isbn']:
            return jsonify({'error': 'El ISBN ya existe'}), 400
        libro.isbn = data['isbn']
    if 'categoria' in data:
        libro.categoria = data['categoria']
    if 'estado' in data:
        libro.estado = data['estado']

    db.session.commit()
    return jsonify({'message': 'Libro actualizado exitosamente'})

@app.route('/libros/<int:id>', methods=['DELETE'])
def delete_libro(id):
    libro = Libro.query.get_or_404(id)
    db.session.delete(libro)
    db.session.commit()
    return jsonify({'message': 'Libro eliminado exitosamente'})

@app.route('/libros/buscar', methods=['GET'])
def search_libros():
    query = Libro.query

    if 'titulo' in request.args:
        query = query.filter(Libro.titulo.ilike(f"%{request.args['titulo']}%"))
    if 'categoria' in request.args:
        query = query.filter(Libro.categoria == request.args['categoria'])

    libros = query.all()
    return jsonify([{
        'id': l.id,
        'titulo': l.titulo,
        'autor': l.autor,
        'isbn': l.isbn,
        'categoria': l.categoria,
        'estado': l.estado,
        'fecha_creacion': l.fecha_creacion.isoformat()
    } for l in libros])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)