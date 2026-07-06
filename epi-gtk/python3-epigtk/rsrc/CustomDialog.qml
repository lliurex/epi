import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
import org.kde.plasma.components 3.0 as PC3
import org.kde.plasma.core 2.0 as PlasmaCore

Dialog {
    id: customDialog

    property alias dialogIcon: dialogIcon.source
    property alias dialogTitle: customDialog.title
    property alias dialogVisible: customDialog.visible
    property alias dialogMsg: dialogText.text
    property alias dialogWidth: container.implicitWidth
    property alias btnAcceptVisible: dialogApplyBtn.visible
    property alias btnCancelText: dialogCancelBtn.text
    property alias btnCancelIcon: dialogCancelBtn.icon.name

    property bool xButton: true

    signal dialogApplyClicked()
    signal cancelDialogClicked()

    modality: Qt.WindowModal

    onVisibleChanged: {
        if (!customDialog.visible && xButton) {
            if (typeof mainStackBridge !== "undefined" && mainStackBridge.showDialog) {
                cancelDialogClicked()
            }
        } else {
            xButton = true
        }
    }

    contentItem: Rectangle {
        id:container
        color: "#ebeced"
        implicitWidth: 550
        implicitHeight: 155

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 15
            spacing: 15

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 15

                PlasmaCore.IconItem {
                    id: dialogIcon
                    source: "dialog-warning"
                    implicitWidth: 64
                    implicitHeight: 64
                }

                Text {
                    id: dialogText
                    font.pointSize: 10
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }

            RowLayout {
                Layout.alignment: Qt.AlignRight | Qt.AlignBottom
                spacing: 10

                PC3.Button {
                    id: dialogApplyBtn
                    display: AbstractButton.TextBesideIcon
                    icon.name: "dialog-ok"
                    text: i18nd("epi-gtk", "Accept")
                    focus: true
                    font.pointSize: 10
                    Keys.onReturnPressed: clicked()
                    Keys.onEnterPressed: clicked()
                    onClicked: {
                        customDialog.xButton = false
                        customDialog.dialogApplyClicked()
                    }
                }

                PC3.Button {
                    id: dialogCancelBtn
                    display: AbstractButton.TextBesideIcon
                    icon.name: "dialog-cancel"
                    text: i18nd("epi-gtk", "Cancel")
                    focus: true
                    font.pointSize: 10
                    Keys.onReturnPressed: clicked()
                    Keys.onEnterPressed: clicked()
                    onClicked: {
                        customDialog.xButton = false
                        customDialog.cancelDialogClicked()
                    }
                }
            }
        }
    }
}
