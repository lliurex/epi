import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3


Rectangle{
    visible: true
    color:"transparent"

    GridLayout{
        id: loadGrid
        rows: 2
        flow: GridLayout.TopToBottom
        anchors.centerIn:parent

        RowLayout{
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter

            Rectangle{
                color:"transparent"
                width:30
                height:30
                
                AnimatedImage{
                    source: "/usr/lib/python3/dist-packages/epigtk/rsrc/loading.gif"
                    transform: Scale {xScale:0.45;yScale:0.45}
                }
            }
        }

        RowLayout{
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter

            Text{
                id:loadtext
                text:getMsg()
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
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

        var msg=""
        switch(mainStackBridge.loadMsgCode){
            case 0:
                msg=i18nd("epi-gtk","Loading information. Wait a moment...")
                break;
            case 1:
                msg=i18nd("epi-gtk","Apt or Dpkg are being executed. Checking if they have finished")
                break;
            case 2:
                msg=i18nd("epi-gtk","Executing the unlocking process. Wait a moment...")
                break
        }
        return msg
    }
}
