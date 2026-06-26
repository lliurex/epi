import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3


Rectangle{
    id: loadRoot
    visible: true
    color:"transparent"

    ColumnLayout{
        id: mainLoaderLayout
        anchors.centerIn: parent
        width: parent.width * 0.9
        spacing: 15

        ColumnLayout{
            Layout.alignment:Qt.AlignHCenter
            spacing:10

            Image{
                id:spinnerImage
                source: "loading.png"
                Layout.preferredWidth: 24
                Layout.preferredHeight: 24
                Layout.alignment: Qt.AlignHCenter
                fillMode: Image.PreserveAspectFit
                smooth:false
                antialiasing:false

                rotation:0
            }
            Timer{
                id:rotationTimer
                running:(spinnerImage!==null && loadRoot!==null) && spinnerImage.visible && loadRoot.visible
                repeat:true
                interval:100

                onTriggered:{
                    spinnerImage.rotation=(spinnerImage.rotation+330)%360   
                }
            }
        
           
            Text{
                id:loadtext
                text:getMsg()
                font.pointSize: 10
                color: palette.windowText
                Layout.alignment:Qt.AlignHCenter
            }
        }
    }

    CustomDialog{
        id:unlockDialog
        dialogIcon:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
        dialogTitle:"EPI"+" - "+i18nd("epi-gtk","Unlock process")
        dialogVisible:mainStackBridge.showDialog
        dialogMsg:i18nd("epi-gtk","Apt or Dpkg seems blocked by a failed previous execution\nClick on Unlock to try to solve the problem") 
        dialogWidth:550
        btnAcceptVisible:false
        btnCancelText:i18nd("epi-gtk","Unlock")
        btnCancelIcon:"dialog-ok"

        Connections{
            target:unlockDialog
            function onCancelDialogClicked(){
                mainStackBridge.launchUnlockProcess()
            } 

        }

    }

    function getMsg(){

        switch(mainStackBridge.loadMsgCode){
            case 0:
                return i18nd("epi-gtk","Loading information. Wait a moment...")
            case 1:
                return i18nd("epi-gtk","Apt or Dpkg are being executed. Checking if they have finished")
            case 2:
                return i18nd("epi-gtk","Executing the unlocking process. Wait a moment...")
        }
    }
}
