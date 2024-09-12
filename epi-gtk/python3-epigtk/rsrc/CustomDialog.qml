import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
//import org.kde.plasma.components 3.0 as PC3

Dialog {
    id: customDialog
    property alias dialogIcon:dialogIcon.source
    property alias dialogTitle:customDialog.title
    property alias dialogVisible:customDialog.visible
    property alias dialogMsg:dialogText.text
    property alias dialogWidth:container.implicitWidth
    property alias btnAcceptVisible:dialogApplyBtn.visible
    property alias btnCancelText:dialogCancelBtn.text
    property alias btnCancelIcon:dialogCancelBtn.icon.name
    property bool xButton
    signal dialogApplyClicked
    signal cancelDialogClicked

    visible:dialogVisible
    title:dialogTitle
    modality:Qt.WindowModal

    
    onVisibleChanged:{
        if (!this.visible && xButton){
            if (mainStackBridge.showDialog){
                cancelDialogClicked()
            }
        }else{
            xButton=true
        }
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
        //PC3.Button {
        Button{
            id:dialogApplyBtn
            display:AbstractButton.TextBesideIcon
            //icon.name:"dialog-ok"
            icon.source:"/usr/share/icons/breeze/actions/22/dialog-ok"
            //text: i18nd("epi-gtk","Accept")
            text:"Accept"
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
                xButton:false
                dialogApplyClicked()
            }
        }

        //PC3.Button {
        Button{
            id:dialogCancelBtn
            display:AbstractButton.TextBesideIcon
            //icon.name: btnCancelIcon
            icon.source:"/usr/share/icons/breeze/actions/22/"+btnCancelIcon
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
                xButton:false
                cancelDialogClicked()
            }
        }  
  
    }
 }
