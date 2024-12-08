#include "selfdrive/ui/sunnypilot/qt/offroad/settings/uem_settings.h"
#include <tuple>
#include <vector>

#include "common/model.h"

UemPanel::UemPanel(QWidget *parent, int edit) : QFrame(parent) {
  main_layout = new QStackedLayout(this);


  ListWidgetSP *list = new ListWidgetSP(this, false);
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "telemetria_uem",
      tr("TELEMETRIA UEM"),
      tr("EXPLICACION TELEMETRIA UEM"),
      "../assets/offroad/icon_blank.png",
    }
    /**
    {
      "toggle_op1",
      tr("op1"),
      tr(""),
      "../assets/offroad/icon_blank.png",
    },
    {
      "toggle_op2",
      tr("op2"),
      tr(""),
      "../assets/offroad/icon_blank.png",
    },
    {
      "toggle_op3",
      tr("op3"),
      tr(""),
      "../assets/offroad/icon_blank.png",
    }*/
  };

  // Subpanel para TELEMETRIA UEM
  SubPanelButton *madsSettings = new SubPanelButton(tr("Conf. TELEMETRIA UEM"));
  madsSettings->setObjectName("mads_btn");
  QVBoxLayout* madsSettingsLayout = new QVBoxLayout;
  madsSettingsLayout->setContentsMargins(0, 0, 0, 30);
  madsSettingsLayout->addWidget(madsSettings);

  // Crear instancia de TelUemSettings y agregarla al layout
  mads_settings = new TelUemSettings(this);  // Instancia de TelUemSettings
  main_layout->addWidget(mads_settings);     // AÑADIR TelUemSettings AL QStackedLayout


SubPanelButton *madsSettings2 = new SubPanelButton(tr("INFO SOFTWARE UEM"));
  madsSettings2->setObjectName("mads_btn2");
  QVBoxLayout* madsSettingsLayout2 = new QVBoxLayout;

  madsSettingsLayout2->setContentsMargins(0, 0, 0, 30);
  madsSettingsLayout2->addWidget(madsSettings2);

  // Crear instancia de TelUemSettings y agregarla al layout
  mads_settings2 = new InfoUem(this);  // Instancia de TelUemSettings
  main_layout->addWidget(mads_settings2);     // AÑADIR TelUemSettings AL QStackedLayout


SubPanelButton *madsSettings3 = new SubPanelButton(tr("Sender UEM"));
  madsSettings3->setObjectName("mads_btn3");
  QVBoxLayout* madsSettingsLayout3 = new QVBoxLayout;

  madsSettingsLayout3->setContentsMargins(0, 0, 0, 30);
  madsSettingsLayout3->addWidget(madsSettings3);

  // Crear instancia de TelUemSettings y agregarla al layout
  mads_settings3 = new SenderUem(this);  // Instancia de TelUemSettings
  main_layout->addWidget(mads_settings3);     // AÑADIR TelUemSettings AL QStackedLayout



  connect(madsSettings, &QPushButton::clicked, [=]() {
    scrollView->setLastScrollPosition();
    main_layout->setCurrentWidget(mads_settings);  // Cambiar al panel de TelUemSettings
  });

  connect(madsSettings2, &QPushButton::clicked, [=]() {
    scrollView->setLastScrollPosition();
    main_layout->setCurrentWidget(mads_settings2);  // Cambiar al panel de TelUemSettings
  });

  connect(madsSettings3, &QPushButton::clicked, [=]() {
    scrollView->setLastScrollPosition();
    main_layout->setCurrentWidget(mads_settings3);  // Cambiar al panel de TelUemSettings
  });

  // Conectar el evento backPress para regresar a la pantalla principal
  connect(mads_settings, &TelUemSettings::backPress, [=]() {
    scrollView->restoreScrollPosition();
    main_layout->setCurrentWidget(sunnypilotScreen);  // Volver a la pantalla principal
  });


    connect(mads_settings2, &InfoUem::backPress, [=]() {
    scrollView->restoreScrollPosition();
    main_layout->setCurrentWidget(sunnypilotScreen);  // Volver a la pantalla principal
  });

     connect(mads_settings3, &SenderUem::backPress, [=]() {
        scrollView->restoreScrollPosition();
        main_layout->setCurrentWidget(sunnypilotScreen);  // Volver a la pantalla principal
      });


  // Añadir toggles y el botón de "Conf. TELEMETRIA UEM"
  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControlSP(param, title, desc, icon, this);
    list->addItem(toggle);
    toggles[param.toStdString()] = toggle;

    if (param == "telemetria_uem") {
      list->addItem(madsSettingsLayout);  // Añadir el botón debajo del toggle de TELEMETRIA UEM



    }
     list->addItem(madsSettingsLayout3);  // Añadir el botón debajo del toggle de TELEMETRIA UEM
      list->addItem(horizontal_line());   // Separador
      list->addItem(madsSettingsLayout2);  // Añadir el botón debajo del toggle de TELEMETRIA UEM


  }

  sunnypilotScreen = new QWidget(this);
  QVBoxLayout* vlayout = new QVBoxLayout(sunnypilotScreen);
  vlayout->setContentsMargins(0, 0, 50, 20);
  scrollView = new ScrollViewSP(list, this);
  vlayout->addWidget(scrollView, 1);
  main_layout->addWidget(sunnypilotScreen);  // AÑADIR la pantalla principal al layout

  // Establecer la pantalla principal como la pantalla predeterminada
  main_layout->setCurrentWidget(sunnypilotScreen);
connect(toggles["telemetria_uem"], &ToggleControlSP::toggleFlipped, [=](bool state) {
    madsSettings->setEnabled(state);
  });
    madsSettings->setEnabled(toggles["telemetria_uem"]->isToggled());

  setStyleSheet(R"(
    #back_btn {
      font-size: 50px;
      margin: 0px;
      padding: 15px;
      border-width: 0;
      border-radius: 30px;
      color: #dddddd;
      background-color: #393939;
    }
    #back_btn:pressed {
      background-color:  #4a4a4a;
    }
  )");
}

void UemPanel::showEvent(QShowEvent *event) {
  updateToggles();
}

void UemPanel::hideEvent(QHideEvent *event) {
  main_layout->setCurrentWidget(sunnypilotScreen);  // Volver a la pantalla principal al ocultar
}

void UemPanel::updateToggles() {


  if (!isVisible()) {
    return;
  }
}
