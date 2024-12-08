#pragma once

#include <QObject>
#include <QLabel>
#include <QTimer>
#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

class SenderUem : public QWidget {
  Q_OBJECT

public:
  explicit SenderUem(QWidget* parent = nullptr);  // Constructor
  void showEvent(QShowEvent* event) override;

signals:
  void backPress();

public slots:
  void updateToggles();  // Método para actualizar la dirección

private:
  QLabel* info_label;       // QLabel para mostrar la dirección
  QLabel* arrow_label;      // QLabel para mostrar la flecha
  QPixmap arrow_pixmap;     // QPixmap para la imagen de la flecha
  Params params;            // Instancia de Params
  QTimer* update_timer;     // Temporizador para actualizaciones en tiempo real
};
