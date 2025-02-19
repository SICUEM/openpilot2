#include "selfdrive/ui/sunnypilot/qt/onroad/buttons.h"

#include "selfdrive/ui/qt/util.h"

static void drawCustomButtonIcon(QPainter &p, const int btn_size_x, const int btn_size_y, const QPixmap &img, const QBrush &bg, float opacity) {
  QPoint center(btn_size_x / 2, btn_size_y / 2);
  p.setRenderHint(QPainter::Antialiasing);
  p.setOpacity(1.0);  // bg dictates opacity of ellipse
  p.setPen(Qt::NoPen);
  p.setBrush(bg);
  p.drawEllipse(center, btn_size_x / 2, btn_size_y / 2);
  p.setOpacity(opacity);
  p.drawPixmap(center - QPoint(img.width() / 2, img.height() / 2), img);
  p.setOpacity(1.0);
}

// **Botón Experimental**
void ExperimentalButtonSP::updateState(const UIStateSP &s) {
  const auto cs = (*s.sm)["controlsState"].getControlsState();
  bool eng = cs.getEngageable() || cs.getEnabled();
  if ((cs.getExperimentalMode() != experimental_mode) || (eng != engageable)) {
    engageable = eng;
    experimental_mode = cs.getExperimentalMode();
    update();
  }
}

// **Botón de Configuración Onroad**
OnroadSettingsButton::OnroadSettingsButton(QWidget *parent) : QPushButton(parent) {
  setFixedSize(152, 152);
  settings_img = loadPixmap("../assets/navigation/icon_settings.svg", {114, 114});

  setVisible(false);
  setEnabled(false);
}

void OnroadSettingsButton::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  drawCustomButtonIcon(p, 152, 152, settings_img, QColor(0, 0, 0, 166), isDown() ? 0.6 : 1.0);
}

void OnroadSettingsButton::updateState(const UIStateSP &s) {
  const auto cp = (*s.sm)["carParams"].getCarParams();
  auto dlp_enabled = s.scene.driving_model_generation == cereal::ModelGeneration::ONE;
  bool allow_btn = s.scene.onroad_settings_toggle && (dlp_enabled || hasLongitudinalControl(cp) || !cp.getPcmCruiseSpeed());

  setVisible(allow_btn);
  setEnabled(allow_btn);
}

// **Botón de Configuración de Mapas**
MapSettingsButton::MapSettingsButton(QWidget *parent) : QPushButton(parent) {
  setFixedSize(152, 152);
  settings_img = loadPixmap("../assets/navigation/icon_directions_outlined.svg", {114, 114});

  setVisible(false);
  setEnabled(false);
}

void MapSettingsButton::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  drawCustomButtonIcon(p, 152, 152, settings_img, QColor(0, 0, 0, 166), isDown() ? 0.6 : 1.0);
}

// **Nuevo botón GirarALaDerecha**
GirarALaDerechaButton::GirarALaDerechaButton(QWidget *parent) : QPushButton(parent) {
  setFixedSize(152, 152);
  girar_img = loadPixmap("../assets/navigation/img_girar_derecha.png", {114, 114});

  QObject::connect(this, &QPushButton::clicked, this, &GirarALaDerechaButton::changeMode);
}

void GirarALaDerechaButton::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  drawCustomButtonIcon(p, 152, 152, girar_img, QColor(0, 0, 0, 166), isDown() ? 0.6 : 1.0);
}

void GirarALaDerechaButton::updateState(const UIStateSP &s) {
  const auto cs = (*s.sm)["controlsState"].getControlsState();
  bool eng = cs.getEngageable() || cs.getEnabled();
  if ((params.getBool("GirarALaDerecha") != girar_a_la_derecha) || (eng != engageable)) {
    engageable = eng;
    girar_a_la_derecha = params.getBool("GirarALaDerecha");
    update();
  }
}

void GirarALaDerechaButton::changeMode() {
  params.putBool("GirarALaDerecha", !girar_a_la_derecha);
}
