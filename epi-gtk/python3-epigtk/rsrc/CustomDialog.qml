import org.kde.kirigami as Kirigami
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.plasma.components as PC

Popup {
    id: customDialog
    property bool dialogVisible: false
    visible:dialogVisible

    property alias dialogIcon:iconInternal.source 
    property alias dialogMsg:dialogText.text
    property int dialogWidth:400
    property alias btnAcceptVisible:dialogApplyBtn.visible
    property alias btnCancelText:dialogCancelBtn.text
    property alias btnCancelIcon:dialogCancelBtn.icon.name
    
    signal dialogApplyClicked
    signal cancelDialogClicked

    modal:true
    anchors.centerIn:Overlay.overlay
    closePolicy:Popup.NoAutoClose

    background:Rectangle{
        color:"#ebeced"
        border.color:"#b8b9ba"
        border.width:1
        radius:5.0
    }
   
    contentItem: Item {
        implicitWidth: customDialog.dialogWidth
        implicitHeight: 120

        RowLayout {
            id: contentRow
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 10
            spacing: 15

            Kirigami.Icon {
                id: iconInternal
                Layout.preferredWidth: 64
                Layout.preferredHeight: 64
            }
        
            Text {
                id:dialogText
                font.pointSize: 10
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                verticalAlignment: Text.AlignVCenter
                color: "#31363b"
            
            }
        }
        RowLayout {
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.margins: 10
            spacing: 10

            PC.Button {
                id: dialogApplyBtn
                icon.name: "dialog-ok"
                text:i18nd("epi-gtk","Accept")
                onClicked: dialogApplyClicked() 
            }

            PC.Button {
                id: dialogCancelBtn
                icon.name: btnCancelIcon
                onClicked: cancelDialogClicked()
            }
        }
    }
}
