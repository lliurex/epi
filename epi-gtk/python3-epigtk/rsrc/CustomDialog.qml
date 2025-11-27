import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.plasma.components as PC

Popup {
    id: customDialog
    property alias dialogIcon:dialogIcon.source
    property alias dialogVisible:customDialog.visible
    property alias dialogMsg:dialogText.text
    property alias dialogWidth:container.implicitWidth
    property alias btnAcceptVisible:dialogApplyBtn.visible
    property alias btnCancelText:dialogCancelBtn.text
    property alias btnCancelIcon:dialogCancelBtn.icon.name
    signal dialogApplyClicked
    signal cancelDialogClicked

    visible:dialogVisible
    modal:true
    anchors.centerIn:Overlay.overlay
    closePolicy:Popup.NoAutoClose

    background:Rectangle{
        color:"#ebeced"
        border.color:"#b8b9ba"
        border.width:1
        radius:5.0
    }
   
    contentItem: Rectangle {
        id:container
        color: "#ebeced"
        implicitWidth: dialogWidth
        implicitHeight: 120
        anchors.topMargin:5
        anchors.leftMargin:5

        Image{
            id:dialogIcon
            source:dialogIcon

        }
        
        Text {
            id:dialogText
            text:dialogMsg
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 10
            anchors.left:dialogIcon.right
            anchors.verticalCenter:dialogIcon.verticalCenter
            anchors.leftMargin:10
        
        }
        PC.Button {
            id:dialogApplyBtn
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-ok"
            text: i18nd("epi-gtk","Accept")
            focus:true
            visible:btnAcceptVisible
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 10
            anchors.bottom:parent.bottom
            anchors.right:dialogCancelBtn.left
            anchors.rightMargin:10
            anchors.bottomMargin:5
            Keys.onReturnPressed: dialogApplyBtn.clicked()
            Keys.onEnterPressed: dialogApplyBtn.clicked()
            onClicked:{
                dialogApplyClicked()
            }
        }

        PC.Button {
            id:dialogCancelBtn
            display:AbstractButton.TextBesideIcon
            icon.name: btnCancelIcon
            text: btnCancelText
            focus:true
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 10
            anchors.bottom:parent.bottom
            anchors.right:parent.right
            anchors.rightMargin:5
            anchors.bottomMargin:5
            Keys.onReturnPressed: dialogCancelBtn.clicked()
            Keys.onEnterPressed: dialogCancelBtn.clicked()
            onClicked:{
                cancelDialogClicked()
            }
        }  
  
    }
 }
