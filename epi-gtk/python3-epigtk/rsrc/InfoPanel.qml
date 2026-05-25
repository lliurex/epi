import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.plasma.components as PC

Rectangle {
    id: root
    color: "transparent"

    ColumnLayout {
        id: infoLayout
        spacing: 5
        anchors.fill: parent
        anchors.leftMargin:5
        anchors.rightMargin:15
        anchors.bottomMargin: 25

        Text {
            text: i18nd("epi-gtk", "Additional information")
            font.pointSize: 16
            Layout.fillWidth: true
        }

        RowLayout {
            spacing: 15
            Layout.topMargin: 15
            Layout.bottomMargin: 10
            Layout.leftMargin:15
            Layout.rightMargin:10
            Layout.fillWidth: true

            Image {
                id: pkgIcon
                source: packageStackBridge.pkgStoreInfo.icon
                sourceSize.width: 64
                sourceSize.height: 64
                mipmap: true
                smooth: true
                fillMode: Image.PreserveAspectFit
                Layout.alignment: Qt.AlignVCenter
            }

            ColumnLayout {
                spacing: 5
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter

                Text {
                    id: pkgNameText
                    text: packageStackBridge.pkgStoreInfo.name
                    font.pointSize: 14
                    horizontalAlignment: Text.AlignLeft
                    Layout.fillWidth: true
                }

                Text {
                    id: pkgSummayText
                    text: packageStackBridge.pkgStoreInfo.summary
                    font.pointSize: 12
                    horizontalAlignment: Text.AlignLeft
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                }
            }
        }

        Rectangle {
            id: container
            color: "transparent"
            clip: true
            Layout.fillWidth: true
            Layout.fillHeight: true

            PC.ScrollView {
                anchors.fill: parent
                anchors.leftMargin: 11
                anchors.rightMargin:10
                contentWidth: availableWidth

                Text {
                    id: pkgDescriptionText
                    text: packageStackBridge.pkgStoreInfo.description
                    font.pointSize: 11
                    horizontalAlignment: Text.AlignLeft
                    width: parent.width
                    wrapMode: Text.WordWrap
                }
            }
        }
    }
}
