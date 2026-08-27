import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

import '../../dominio/entidades/evento_impacto.dart';

/// Cola local sin conexión (RF-04).
///
/// Todo evento se guarda aquí PRIMERO, sin importar si hay red o no.
/// La sincronización es un proceso aparte que intenta subir lo pendiente;
/// si falla, el evento simplemente sigue esperando en la cola.
class ColaLocal {
  static Database? _db;

  Future<Database> _abrir() async {
    if (_db != null) return _db!;
    final ruta = join(await getDatabasesPath(), 'bitacora_sismica.db');
    _db = await openDatabase(
      ruta,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE evento_impacto (
            id_local INTEGER PRIMARY KEY AUTOINCREMENT,
            id_remoto TEXT,
            clave_cliente TEXT NOT NULL UNIQUE,
            magnitud REAL NOT NULL,
            severidad TEXT NOT NULL,
            latitud REAL,
            longitud REAL,
            precision_m REAL,
            ocurrido_en TEXT NOT NULL,
            sincronizado INTEGER NOT NULL DEFAULT 0
          )
        ''');
        await db.execute(
          'CREATE INDEX idx_evento_sincronizado ON evento_impacto(sincronizado)',
        );
        await db.execute('''
          CREATE TABLE IF NOT EXISTS configuracion (
            clave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
          )
        ''');
      },
    );
    return _db!;
  }

  Future<String> obtenerOEstablecerDispositivoId(String fallbackUuid) async {
    final db = await _abrir();
    final filas = await db.query(
      'configuracion',
      where: 'clave = ?',
      whereArgs: ['dispositivo_id'],
    );
    if (filas.isNotEmpty) {
      return filas.first['valor'] as String;
    }
    await db.insert('configuracion', {
      'clave': 'dispositivo_id',
      'valor': fallbackUuid,
    });
    return fallbackUuid;
  }

  Future<void> encolar(EventoImpacto evento) async {
    final db = await _abrir();
    await db.insert(
      'evento_impacto',
      evento.aMapaLocal(),
      conflictAlgorithm: ConflictAlgorithm.ignore, // clave_cliente repetida = no-op
    );
  }

  Future<List<EventoImpacto>> pendientes() async {
    final db = await _abrir();
    final filas = await db.query(
      'evento_impacto',
      where: 'sincronizado = 0',
      orderBy: 'ocurrido_en ASC',
    );
    return filas.map(EventoImpacto.desdeMapaLocal).toList();
  }

  Future<void> marcarSincronizado(String claveCliente, {String? idRemoto}) async {
    final db = await _abrir();
    await db.update(
      'evento_impacto',
      {'sincronizado': 1, if (idRemoto != null) 'id_remoto': idRemoto},
      where: 'clave_cliente = ?',
      whereArgs: [claveCliente],
    );
  }

  Future<List<EventoImpacto>> historico({int limite = 50}) async {
    final db = await _abrir();
    final filas = await db.query(
      'evento_impacto',
      orderBy: 'ocurrido_en DESC',
      limit: limite,
    );
    return filas.map(EventoImpacto.desdeMapaLocal).toList();
  }
}
