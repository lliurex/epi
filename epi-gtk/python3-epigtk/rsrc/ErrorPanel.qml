import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.16 as Kirigami

Rectangle{
    visible: true
    color:"transparent"

    GridLayout{
        id: loadGrid
        rows: 2
        rowSpacing:10
        flow: GridLayout.TopToBottom
        anchors.centerIn:parent
        property var warningCode:[-10,-11]

        Kirigami.InlineMessage {
            id: errorLabel
            visible:true
            text:getErrorText(mainStackBridge.loadErrorCode)
            type:{
                if (loadGrid.warningCode.includes(mainStackBridge.loadErrorCode)){
                    Kirigami.MessageType.Warning;
                }else{
                    Kirigami.MessageType.Error;
                }
            }
            Layout.minimumWidth:770
            Layout.fillWidth:true
            Layout.rightMargin:15
            Layout.leftMargin:15
        }

        Text{
            id:loadtext
            //text:i18nd("epi-gtk","Addittional information:\n")+mainStackBridge.localDebError
            text:"Addittional information:\n"+mainStackBridge.localDebError
            visible:{
                if (mainStackBridge.localDebError!=""){
                    true
                }else{
                    false
                }
            }
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 10
            Layout.alignment:Qt.AlignLeft
            Layout.leftMargin:15
            Layout.fillWidth:true
        }
    }

    function getErrorText(code){

        var msg=""
        switch (code){
            case -1:
                //msg=i18nd("epi-gtk","Application epi file does not exist or its path is invalid");
                msg="Application epi file does not exist or its path is invalid";
                break;
            case -2:
                //msg=i18nd("epi-gtk","Application epi file is empty")
                msg="Application epi file is empty"
                break;
            case -3:
                //msg=i18nd("epi-gtk","Application epi file it is not a valid json")
                msg="Application epi file it is not a valid json"
                break;
            case -4:
                //msg=i18nd("epi-gtk","Associated script does not exist or its path is invalid")
                msg="Associated script does not exist or its path is invalid"
                break;
            case -5:
                //msg=i18nd("epi-gtk","Associated script does not have execute permissions")
                msg="Associated script does not have execute permissions"
                break;
            case -6:
                //msg=i18nd("epi-gtk","You need root privileges")
                msg="You need root privileges"
                break;
            case -7:
                //msg=i18nd("epi-gtk","The package will not be able to be installed\nAn error occurred during processing")
                msg="The package will not be able to be installed\nAn error occurred during processing"
                break;
            case -8:
                //msg=i18nd("epi-gtk","The package will not be able to be installed. Problems with dependencies")
                msg="The package will not be able to be installed. Problems with dependencies"
                break;
            case -9:
                //msg=i18nd("epi-gtk","The package will not be able to be installed. Error has been detected")
                msg="The package will not be able to be installed. Error has been detected"
                break;
            case -10:
                //msg=i18nd("epi-gtk","The system is being updated. Wait a few minutes and try again")
                msg="The system is being updated. Wait a few minutes and try again"
                break;
            case -11:
               //msg=i18nd("epi-gtk","Apt or Dpkg are being executed. Wait a few minutes and try again")
                msg="Apt or Dpkg are being executed. Wait a few minutes and try again"
                break;
            case -13:
                //msg=i18nd("epi-gtk","The unlocking process has failed")
                msg="The unlocking process has failed"
                break;
        }
        return msg
    }
}
