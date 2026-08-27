import 'dart:async';
import 'dart:math';

import 'package:flutter/services.dart';
import 'package:geolocator/geolocator.dart';
import 'package:sensors_plus/sensors_plus.dart';
import 'package:uuid/uuid.dart';

import '../../dominio/entidades/evento_impacto.dart';
import '../local/cola_local.dart';
import 'api_eventos.dart';

/// Detecta impactos usando el acelerómetro SIN gravedad (RF-01),
/// adjunta la coordenada del GPS (RF-02), confirma con vibración
/// diferenciada (RF-03) y guarda todo localmente antes de intentar
/// subirlo (RF-04).
///
/// El umbral y el tiempo de reposo son constantes con nombre:
/// documenta en docs/decisiones.md por qué quedaron en estos valores
/// (la guía sugiere partir de 15.0 y 900 ms, y ajustarlos según
/// pruebas reales en el equipo de gama baja disponible).
class VigiaImpactos {
  final ColaLocal cola;
  final ApiEventos api;
  final double umbral;
  final Duration reposo;
  static const _uuid = Uuid();

  DateTime _ultimo = DateTime.fromMillisecondsSinceEpoch(0);
  StreamSubscription<UserAccelerometerEvent>? _sub;

  final _controladorEventos = StreamController<EventoImpacto>.broadcast();
  Stream<EventoImpacto> get eventos => _controladorEventos.stream;

  VigiaImpactos({
    required this.cola,
    required this.api,
    this.umbral = 15.0,
    this.reposo = const Duration(milliseconds: 900),
  });

  void iniciar() {
    _sub = userAccelerometerEventStream(
      samplingPeriod: SensorInterval.gameInterval,
    ).listen((evento) {
      final magnitud = sqrt(
        evento.x * evento.x + evento.y * evento.y + evento.z * evento.z,
      );
      if (_esImpactoNuevo(magnitud)) {
        _registrar(magnitud);
      }
    });
  }

  bool _esImpactoNuevo(double magnitud) {
    if (magnitud < umbral) return false;
    final ahora = DateTime.now();
    if (ahora.difference(_ultimo) < reposo) return false;
    _ultimo = ahora;
    return true;
  }

  Future<void> _registrar(double magnitud) async {
    final severidad = magnitud < 20
        ? 'leve'
        : magnitud < 35
            ? 'moderado'
            : 'fuerte';

    // Retroalimentación háptica diferenciada (RF-03).
    if (severidad == 'fuerte') {
      HapticFeedback.heavyImpact();
    } else {
      HapticFeedback.lightImpact();
    }

    Position? posicion;
    try {
      posicion = await _obtenerPosicion();
    } catch (_) {
      posicion = null; // El evento vale aunque no haya GPS disponible.
    }

    final evento = EventoImpacto(
      claveCliente: _uuid.v4(),
      magnitud: magnitud,
      severidad: severidad,
      latitud: posicion?.latitude,
      longitud: posicion?.longitude,
      precisionM: posicion?.accuracy,
      ocurridoEn: DateTime.now().toUtc(),
    );

    // Primero local: el evento nunca se pierde, exista o no la red.
    await cola.encolar(evento);
    _controladorEventos.add(evento);

    // Intento de sincronización en segundo plano; si falla, no bloquea nada.
    unawaited(api.sincronizarPendientes());
  }

  Future<Position?> _obtenerPosicion() async {
    final permiso = await _asegurarPermisoUbicacion();
    if (!permiso) return null;

    try {
      return await Geolocator.getLastKnownPosition() ??
          await Geolocator.getCurrentPosition(
            locationSettings: const LocationSettings(
              accuracy: LocationAccuracy.high,
            ),
          ).timeout(const Duration(seconds: 4));
    } catch (_) {
      return null;
    }
  }

  Future<bool> _asegurarPermisoUbicacion() async {
    if (!await Geolocator.isLocationServiceEnabled()) return false;
    var permiso = await Geolocator.checkPermission();
    if (permiso == LocationPermission.denied) {
      permiso = await Geolocator.requestPermission();
    }
    return permiso == LocationPermission.always ||
        permiso == LocationPermission.whileInUse;
  }

  Future<void> detener() async {
    await _sub?.cancel();
    _sub = null;
  }

  void dispose() {
    _controladorEventos.close();
  }
}
