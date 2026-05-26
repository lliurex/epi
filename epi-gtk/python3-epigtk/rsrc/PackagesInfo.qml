import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


Rectangle{
    color:"transparent"

    ColumnLayout{
        id:generalPackagesLayout
        spacing: 5
        anchors.fill:parent
        anchors.leftMargin:5
        anchors.rightMargin:15
        anchors.bottomMargin:10

        Text{ 
            text:i18nd("epi-gtk","Applications availables")
            font.pointSize: 16

        }
        
        PackagesList{
            id:packagesList
            Layout.fillHeight:true
            Layout.fillWidth:true
            packagesModel:packageStackBridge.packagesModel
        }
    
    }

} 
