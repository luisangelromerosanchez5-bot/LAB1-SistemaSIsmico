import 'package:flutter/material.dart';

import '../../datos/local/cola_local.dart';
import '../../datos/servicios/api_eventos.dart';
import '../../datos/servicios/identidad_dispositivo.dart';
import '../../datos/servicios/vigia_impactos.dart';
import '../../dominio/entidades/evento_impacto.dart';

class PaginaBitacora extends StatefulWidget {
  const PaginaBitacora({super.key});

  @override
  State<PaginaBitacora> createState() => _PaginaBitacoraState();
}

class _PaginaBitacoraState extends State<PaginaBitacora> {
  late final ColaLocal _cola;
  VigiaImpactos? _vigia;

  bool _monitoreando = false;
  bool _cargando = true;
  final List<EventoImpacto> _eventos = [];

  @override
  void initState() {
    super.initState();
    _cola = ColaLocal();
    _inicializarServicios();
  }

  Future<void> _inicializarServicios() async {
    final identidad = IdentidadDispositivo(cola: _cola);
    final dispositivoId = await identidad.obtenerDispositivoId();
    final api = ApiEventos(dispositivoId: dispositivoId);
    final vigia = VigiaImpactos(cola: _cola, api: api);
    
    vigia.eventos.listen((evento) {
      if (mounted) {
        setState(() => _eventos.insert(0, evento));
      }
    });

    if (mounted) {
      setState(() {
        _vigia = vigia;
        _cargando = false;
      });
    }

    await _cargarHistorico();
  }

  Future<void> _cargarHistorico() async {
    final historico = await _cola.historico();
    if (mounted) {
      setState(() {
        _eventos
          ..clear()
          ..addAll(historico);
      });
    }
  }

  void _alternarMonitoreo() {
    if (_vigia == null) return;
    setState(() => _monitoreando = !_monitoreando);
    if (_monitoreando) {
      _vigia!.iniciar();
    } else {
      _vigia!.detener(); // CRÍTICO: cancelar la suscripción al salir/detener.
    }
  }

  @override
  void dispose() {
    _vigia?.detener();
    _vigia?.dispose();
    super.dispose();
  }

  Color _colorSeveridad(String severidad) => switch (severidad) {
        'fuerte' => Colors.red,
        'moderado' => Colors.orange,
        _ => Colors.green,
      };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Bitácora sísmica CEET')),
      body: _cargando
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      Icon(
                        _monitoreando ? Icons.sensors : Icons.sensors_off,
                        size: 56,
                        color: _monitoreando ? Colors.green : Colors.grey,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _monitoreando ? 'Monitoreando impactos…' : 'Monitoreo detenido',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 12),
                      FilledButton.icon(
                        onPressed: _alternarMonitoreo,
                        icon: Icon(_monitoreando ? Icons.stop : Icons.play_arrow),
                        label: Text(_monitoreando ? 'Detener' : 'Iniciar'),
                      ),
                    ],
                  ),
                ),
                const Divider(height: 1),
                Expanded(
                  child: _eventos.isEmpty
                      ? const Center(child: Text('Aún no se han registrado impactos.'))
                      : ListView.builder(
                          itemCount: _eventos.length,
                          itemBuilder: (context, i) {
                            final e = _eventos[i];
                            return ListTile(
                              leading: CircleAvatar(
                                backgroundColor: _colorSeveridad(e.severidad),
                                child: Text(e.magnitud.toStringAsFixed(0)),
                              ),
                              title: Text('Severidad: ${e.severidad}'),
                              subtitle: Text(
                                '${e.ocurridoEn.toLocal()}'
                                '${e.latitud != null ? '\n${e.latitud!.toStringAsFixed(5)}, ${e.longitud!.toStringAsFixed(5)}' : '\nSin ubicación'}',
                              ),
                              trailing: Icon(
                                e.sincronizado ? Icons.cloud_done : Icons.cloud_upload,
                                color: e.sincronizado ? Colors.green : Colors.grey,
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
    );
  }
}
