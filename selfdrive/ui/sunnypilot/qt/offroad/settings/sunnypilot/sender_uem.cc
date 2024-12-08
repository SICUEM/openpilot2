#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sunnypilot/sender_uem.h"

#include <QLabel>
#include <QPixmap>
#include <QTimer>
#include <QTransform>

SenderUem::SenderUem(QWidget* parent) : QWidget(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);
  main_layout->setSpacing(20);

  // Botón de retroceso
  PanelBackButton* back = new PanelBackButton();
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  // Añade la imagen de la flecha
  arrow_label = new QLabel(this);
  arrow_pixmap = QPixmap("../assets/navigation/arrow.svg");  // Cargar la imagen de la flecha
  arrow_label->setPixmap(arrow_pixmap);
  arrow_label->setAlignment(Qt::AlignCenter);
  main_layout->addWidget(arrow_label, 1, Qt::AlignCenter);

  // Añade el texto con los integrantes de SICUEM
  info_label = new QLabel("Direccion", this);
  main_layout->addWidget(info_label, 0, Qt::AlignCenter);

  // Configurar el temporizador para actualizar en tiempo real
  update_timer = new QTimer(this);
  connect(update_timer, &QTimer::timeout, this, &SenderUem::updateToggles);
  update_timer->start(100);  // Actualiza cada 100 ms (0.1 segundos)
}

void SenderUem::showEvent(QShowEvent* event) {
  QWidget::showEvent(event);
  updateToggles();
}

void SenderUem::updateToggles() {
  if (!isVisible()) {
    return;
  }

  QString direction = "Direccion";  // Valor por defecto
  QTransform transform;  // Objeto para la transformación

  // Verificar los parámetros y actualizar la dirección y la rotación
  if (params.getBool("sender_uem_up")) {
    direction = "Up";
    transform.rotate(0);  // No rotar para "Up"
  } else if (params.getBool("sender_uem_down")) {
    direction = "Down";
    transform.rotate(180);  // Rotar 180 grados para "Down"
  } else if (params.getBool("sender_uem_left")) {
    direction = "Left";
    transform.rotate(270);  // Rotar 270 grados para "Left"
  } else if (params.getBool("sender_uem_right")) {
    direction = "Right";
    transform.rotate(90);  // Rotar 90 grados para "Right"
  }

  // Actualizar el QLabel con la dirección
  info_label->setText(direction);

  // Rotar y actualizar la imagen de la flecha
  QPixmap rotated_pixmap = arrow_pixmap.transformed(transform);
  arrow_label->setPixmap(rotated_pixmap);
}
