import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../../dominio/entidades/evento_impacto.dart';
import '../local/cola_local.dart';

/// Habla con la API FastAPI y sincroniza la cola pendiente (RF-05).
///
/// IMPORTANTE: cambia [baseUrl] por la dirección real de tu backend.
/// - Emulador Android -> http://10.0.2.2:8000 (10.0.2.2 apunta al localhost de tu PC)
/// - Celular físico en la misma red -> http://<ip-de-tu-pc>:8000
class ApiEventos {
  final Dio _dio;
  final ColaLocal _cola;
  String dispositivoId;

  ApiEventos({
    required this.dispositivoId,
    String baseUrl = 'https://bitacora-sismica-api.onrender.com',
    ColaLocal? cola,
  })  : _cola = cola ?? ColaLocal(),
        _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 8),
          receiveTimeout: const Duration(seconds: 8),
        ));

  Future<void> asegurarRegistroDispositivo() async {
    try {
      final respuesta = await _dio.post(
        '/api/dispositivos',
        data: {
          'identificador': dispositivoId,
          'modelo': 'Android Device',
        },
      );
      if (respuesta.data != null && respuesta.data['id'] != null) {
        final serverId = respuesta.data['id'] as String;
        dispositivoId = serverId;
        await _cola.sobrescribirDispositivoId(serverId);
      }
    } catch (e) {
      debugPrint('Aviso registro dispositivo: $e');
    }
  }

  Future<void> sincronizarPendientes() async {
    final List<EventoImpacto> pendientes = await _cola.pendientes();
    if (pendientes.isEmpty) return;

    await asegurarRegistroDispositivo();

    for (final evento in pendientes) {
      try {
        final respuesta = await _dio.post(
          '/api/eventos',
          data: evento.aJsonApi(dispositivoId),
        );
        final idRemoto = respuesta.data['id'] as String?;
        await _cola.marcarSincronizado(evento.claveCliente, idRemoto: idRemoto);
      } on DioException catch (e) {
        debugPrint('Error de sincronización con Render: ${e.response?.statusCode} - ${e.response?.data}');
        return;
      }
    }
  }
}
