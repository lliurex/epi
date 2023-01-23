import org.kde.plasma.core 2.1 as PlasmaCore
import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


Rectangle{
    color:"transparent"
    Text{ 
        text:i18nd("epi-gtk","Applications availables")
        font.family: "Quattrocento Sans Bold"
        font.pointSize: 16
    }

    GridLayout{
        id:generalPackagesLayout
        rows:1
        flow: GridLayout.TopToBottom
        rowSpacing:10
        anchors.left:parent.left
        width:parent.width-10
        height:parent.height-25
        enabled:true

        PackagesList{
            id:packagesList
            Layout.fillHeight:true
            Layout.fillWidth:true
            packagesModel:epiBridge.packagesModel
        }
    
    }

} 
