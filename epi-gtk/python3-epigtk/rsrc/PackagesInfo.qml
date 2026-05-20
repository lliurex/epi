import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


Rectangle{
    color:"transparent"
    Layout.fillWidth:true
    Layout.fillHeight:true

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
