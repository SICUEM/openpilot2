/**
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
***/

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sunnypilot/teluem_settings.h"

#include <tuple>
#include <vector>

TelUemSettings::TelUemSettings(QWidget* parent) : QWidget(parent) {

  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);
  main_layout->setSpacing(20);

  // Back button
  PanelBackButton* back = new PanelBackButton();
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);





  ListWidgetSP *list = new ListWidgetSP(this, false);
  // param, title, desc, icon
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "carState_toggle",
      tr("CarState UEM"),
      tr("Descripción del OPCION 2."),
      "../assets/navigation/uem_logo.svg",
    },{
      "carControl_toggle",
      tr("carControl UEM"),
      tr("Descripción del OPCION 2."),
      "../assets/navigation/uem_logo.svg",
    },
    {
      "gpsLocationExternal_toggle",
      tr("GPSLocation UEM"),
      tr("Descripción del OPCION 3."),
      "../assets/navigation/uem_logo.svg",
    },
     {
      "navInstruction_toggle",
      tr("navInstruction UEM"),
      tr("Descripción del OPCION 4."),
      "../assets/navigation/uem_logo.svg",
    },{
      "radarState_toggle",
      tr("radarState UEM"),
      tr("Descripción del OPCION 4."),
      "../assets/navigation/uem_logo.svg",
    },{
      "drivingModelData_toggle",
      tr("drivingModelData UEM"),
      tr("Descripción del OPCION 4."),
      "../assets/navigation/uem_logo.svg",
    },{
      "mapbox_toggle",
      tr("RESPUESTA MAPBOX "),
      tr("Descripción del OPCION 4."),
      "../assets/navigation/uem_logo.svg",
    }
  };


  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControlSP(param, title, desc, icon, this);

    list->addItem(toggle);
    toggles[param.toStdString()] = toggle;

    // trigger offroadTransition when going onroad/offroad
    //connect(uiStateSP(), &UIStateSP::offroadTransition, toggle, &ParamControlSP::setEnabled);
  }

  // trigger offroadTransition when going onroad/offroad

  main_layout->addWidget(new ScrollViewSP(list, this));


}

void TelUemSettings::showEvent(QShowEvent *event) {
  updateToggles();
}

void TelUemSettings::updateToggles() {
  if (!isVisible()) {
    return;
  }
}
