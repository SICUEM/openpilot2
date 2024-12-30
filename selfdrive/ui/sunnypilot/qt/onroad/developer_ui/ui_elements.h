#pragma once

#include <QColor>
#include <QString>

struct UiElement {
  QString value{};
  QString label{};
  QString units{};
  QColor color{};
  QString iconPath{};  // Nueva ruta del archivo SVG

  explicit UiElement(const QString &value = "", const QString &label = "", const QString &units = "",
                     const QColor &color = QColor(255, 255, 255, 255), const QString &iconPath = "")
    : value(value), label(label), units(units), color(color), iconPath(iconPath) {}
};
