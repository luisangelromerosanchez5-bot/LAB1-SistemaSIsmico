import 'package:flutter/material.dart';

import 'presentacion/paginas/pagina_bitacora.dart';

void main() {
  runApp(const AppBitacoraSismica());
}

class AppBitacoraSismica extends StatelessWidget {
  const AppBitacoraSismica({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Bitácora Sísmica CEET',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.indigo,
        useMaterial3: true,
      ),
      home: const PaginaBitacora(),
    );
  }
}
