import 'package:flutter_test/flutter_test.dart';
import 'package:bitacora_sismica/main.dart';

void main() {
  testWidgets('Carga inicial de la AppBitacoraSismica', (WidgetTester tester) async {
    await tester.pumpWidget(const AppBitacoraSismica());
    expect(find.byType(AppBitacoraSismica), findsOneWidget);
  });
}
