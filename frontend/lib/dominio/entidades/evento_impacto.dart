/// Representa un evento de impacto detectado por el acelerómetro.
///
/// `claveCliente` es la clave de idempotencia: un UUID generado en el
/// propio celular. El servidor la usa para no duplicar el registro si
/// la app reintenta el envío tras un corte de red (ver RF-04/RF-05
/// y el criterio bloqueante de idempotencia de P1).
class EventoImpacto {
  final String? id; // asignado por el servidor una vez sincronizado
  final String claveCliente;
  final double magnitud;
  final String severidad; // 'leve' | 'moderado' | 'fuerte'
  final double? latitud;
  final double? longitud;
  final double? precisionM;
  final DateTime ocurridoEn;
  final bool sincronizado;

  const EventoImpacto({
    this.id,
    required this.claveCliente,
    required this.magnitud,
    required this.severidad,
    this.latitud,
    this.longitud,
    this.precisionM,
    required this.ocurridoEn,
    this.sincronizado = false,
  });

  EventoImpacto copiarCon({String? id, bool? sincronizado}) => EventoImpacto(
        id: id ?? this.id,
        claveCliente: claveCliente,
        magnitud: magnitud,
        severidad: severidad,
        latitud: latitud,
        longitud: longitud,
        precisionM: precisionM,
        ocurridoEn: ocurridoEn,
        sincronizado: sincronizado ?? this.sincronizado,
      );

  Map<String, dynamic> aMapaLocal() => {
        'clave_cliente': claveCliente,
        'magnitud': magnitud,
        'severidad': severidad,
        'latitud': latitud,
        'longitud': longitud,
        'precision_m': precisionM,
        'ocurrido_en': ocurridoEn.toIso8601String(),
        'sincronizado': sincronizado ? 1 : 0,
      };

  factory EventoImpacto.desdeMapaLocal(Map<String, dynamic> mapa) => EventoImpacto(
        id: mapa['id_remoto'] as String?,
        claveCliente: mapa['clave_cliente'] as String,
        magnitud: (mapa['magnitud'] as num).toDouble(),
        severidad: mapa['severidad'] as String,
        latitud: (mapa['latitud'] as num?)?.toDouble(),
        longitud: (mapa['longitud'] as num?)?.toDouble(),
        precisionM: (mapa['precision_m'] as num?)?.toDouble(),
        ocurridoEn: DateTime.parse(mapa['ocurrido_en'] as String),
        sincronizado: (mapa['sincronizado'] as int) == 1,
      );

  /// Cuerpo que espera el endpoint POST /api/eventos de la API.
  Map<String, dynamic> aJsonApi(String dispositivoId) => {
        'dispositivo_id': dispositivoId,
        'clave_cliente': claveCliente,
        'magnitud': magnitud,
        'severidad': severidad,
        'latitud': latitud,
        'longitud': longitud,
        'precision_m': precisionM,
        'ocurrido_en': ocurridoEn.toIso8601String(),
      };
}
