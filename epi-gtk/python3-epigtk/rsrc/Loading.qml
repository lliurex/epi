import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


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
                source: "/usr/lib/python3/dist-packages/epigtk/rsrc/loading.png"
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

                    if (spinnerImage && typeof spinnerImage.rotation!="undefined"){
                        var nextRotation= spinnerImage.rotation-30

                            if (nextRotation<0){
                                nextRotation=330
                            }
                            spinnerImage.rotation=nextRotation
                     }else{
                        stop()
                     }   

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
        dialogIcon:"dialog-warning"
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
