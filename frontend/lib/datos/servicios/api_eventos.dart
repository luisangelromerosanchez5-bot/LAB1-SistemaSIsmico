import 'package:dio/dio.dart';

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
  final String dispositivoId;

  ApiEventos({
    required this.dispositivoId,
    String baseUrl = 'https://bitacora-sismica-api.onrender.com',
    ColaLocal? cola,
  })  : _cola = cola ?? ColaLocal(),
        _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 5),
          receiveTimeout: const Duration(seconds: 5),
        ));

  Future<void> sincronizarPendientes() async {
    final List<EventoImpacto> pendientes = await _cola.pendientes();
    if (pendientes.isEmpty) return;

    for (final evento in pendientes) {
      try {
        final respuesta = await _dio.post(
          '/api/eventos',
          data: evento.aJsonApi(dispositivoId),
        );
        final idRemoto = respuesta.data['id'] as String?;
        await _cola.marcarSincronizado(evento.claveCliente, idRemoto: idRemoto);
      } on DioException catch (e) {
        print('Error de sincronización con Render: ${e.response?.statusCode} - ${e.response?.data}');
        return;
      }
    }
  }
}
