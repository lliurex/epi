import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.16 as Kirigami

Rectangle{
    visible: true
    color:"transparent"

    ColumnLayout{
        id: mainLoaderLayout
        anchors.centerIn: parent
        width: parent.width * 0.9
        spacing: 15
        property var warningCode:[-10,-11]

        Kirigami.InlineMessage {
            id: errorLabel
            visible:true
            text:getErrorText(mainStackBridge.loadErrorCode)
            type:{
                if (mainLoaderLayout.warningCode.includes(mainStackBridge.loadErrorCode)){
                    Kirigami.MessageType.Warning
                }else{
                    Kirigami.MessageType.Error
                }
            }
            Layout.fillWidth:true

        }

        Text{
            id:loadtext
            text:i18nd("epi-gtk","Addittional information:\n")+mainStackBridge.additionalErrorInfo
            visible:mainStackBridge.additionalErrorInfo!=""?true:false
            font.pointSize: 10
            Layout.alignment:Qt.AlignLeft
            Layout.leftMargin:15
            Layout.fillWidth:true
        }
    }

    function getErrorText(code){

        switch (code){
            case -1:
                return i18nd("epi-gtk","Application epi file does not exist or its path is invalid")
            case -2:
                return i18nd("epi-gtk","Application epi file is empty")
            case -3:
                return i18nd("epi-gtk","Application epi file it is not a valid json")
            case -4:
                return i18nd("epi-gtk","Associated script does not exist or its path is invalid")
            case -5:
                return i18nd("epi-gtk","Associated script does not have execute permissions")
            case -6:
                return i18nd("epi-gtk","You need root privileges")
            case -7:
                return i18nd("epi-gtk","The package will not be able to be installed\nAn error occurred during processing")
            case -8:
                return i18nd("epi-gtk","The package will not be able to be installed. Problems with dependencies")
            case -9:
                return i18nd("epi-gtk","The package will not be able to be installed. Error has been detected")
            case -10:
                return i18nd("epi-gtk","The system is being updated. Wait a few minutes and try again")
            case -11:
                return i18nd("epi-gtk","Apt or Dpkg are being executed. Wait a few minutes and try again")
            case -13:
                return i18nd("epi-gtk","The unlocking process has failed")
            case -24:
                return i18nd("epi-gtk","Application epi file it is not a valid json. Missing some keys or keys with incorrect value in json definition. Run in debug mode for more information")
            case -25:
                return i18nd("epi-gtk","A problem has been detected with the dependency's .epi file. Run in debug mode for more information")
        }
    }
}
