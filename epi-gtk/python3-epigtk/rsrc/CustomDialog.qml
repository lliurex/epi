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
        id: container
        color: "#ebeced"
        implicitHeight: 120

        PlasmaCore.IconItem {
            id: dialogIcon
            width: 64
            height: 64
            anchors.left: parent.left
            anchors.top: parent.top

        }

        Text {
            id: dialogText
            font.pointSize: 10
            anchors.left: dialogIcon.right
            anchors.verticalCenter: dialogIcon.verticalCenter
            anchors.leftMargin: 15
            anchors.right: parent.right
            anchors.rightMargin: 15
            wrapMode: Text.WordWrap
        }

        PC3.Button {
            id: dialogApplyBtn
            display: AbstractButton.TextBesideIcon
            icon.name: "dialog-ok"
            text: i18nd("epi-gtk", "Accept")
            focus: true
            font.pointSize: 10

            anchors.bottom: parent.bottom
            anchors.right: dialogCancelBtn.left
            anchors.rightMargin: 10
            anchors.bottomMargin: 10

            Keys.onReturnPressed: dialogApplyBtn.clicked()
            Keys.onEnterPressed: dialogApplyBtn.clicked()

            onClicked: {
                xButton = false
                customDialog.dialogApplyClicked()
            }
        }

        PC3.Button {
            id: dialogCancelBtn
            display: AbstractButton.TextBesideIcon
            focus: true
            font.pointSize: 10

            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.rightMargin: 15
            anchors.bottomMargin: 10

            Keys.onReturnPressed: dialogCancelBtn.clicked()
            Keys.onEnterPressed: dialogCancelBtn.clicked()

            onClicked: {
                xButton = false
                customDialog.cancelDialogClicked()
            }
        }
    }
}
