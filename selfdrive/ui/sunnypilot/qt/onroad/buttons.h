#pragma once

#include <QPushButton>
#include "selfdrive/ui/qt/onroad/buttons.h"

#include "selfdrive/ui/sunnypilot/ui.h"

#include "selfdrive/ui/ui.h"

class ExperimentalButtonSP : public ExperimentalButton {
  Q_OBJECT

public:
  explicit ExperimentalButtonSP(QWidget *parent = nullptr) : ExperimentalButton(parent) {};
  void updateState(const UIStateSP &s);
};

class OnroadSettingsButton : public QPushButton {
  Q_OBJECT

public:
  explicit OnroadSettingsButton(QWidget *parent = nullptr);
  void updateState(const UIStateSP &s);

private:
  void paintEvent(QPaintEvent *event) override;

  QPixmap settings_img;
};

class MapSettingsButton : public QPushButton {
  Q_OBJECT

public:
  explicit MapSettingsButton(QWidget *parent = nullptr);

private:
  void paintEvent(QPaintEvent *event) override;

  QPixmap settings_img;
};

// **Nuevo botón GirarALaDerechaButton**
class GirarALaDerechaButton : public QPushButton {
  Q_OBJECT

public:
  explicit GirarALaDerechaButton(QWidget *parent = nullptr);
  void updateState(const UIStateSP &s);

private:
  void paintEvent(QPaintEvent *event) override;
  void changeMode();

  bool girar_a_la_derecha;
  bool engageable;
  Params params;

  QPixmap girar_img;
};
