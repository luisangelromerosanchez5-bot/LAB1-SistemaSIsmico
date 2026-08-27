import 'package:uuid/uuid.dart';
import '../local/cola_local.dart';

/// Servicio responsable de gestionar el identificador único UUID del dispositivo.
///
/// Cumple con la validación UUID exigida por la API de FastAPI (POST /api/eventos).
class IdentidadDispositivo {
  final ColaLocal _cola;
  static const _uuidGen = Uuid();

  IdentidadDispositivo({ColaLocal? cola}) : _cola = cola ?? ColaLocal();

  /// Obtiene o genera un UUID v4 persistente para este dispositivo.
  Future<String> obtenerDispositivoId() async {
    final nuevoUuid = _uuidGen.v4();
    final guardado = await _cola.obtenerOEstablecerDispositivoId(nuevoUuid);
    try {
      Uuid.parse(guardado);
      return guardado;
    } catch (_) {
      await _cola.sobrescribirDispositivoId(nuevoUuid);
      return nuevoUuid;
    }
  }
}
