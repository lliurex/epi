import org.kde.plasma.core 2.1 as PlasmaCore
import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


GridLayout{
    id:generalPkgLayout
    rows:1
    flow: GridLayout.TopToBottom
    rowSpacing:10
 
    StackView{
        id:generalPkgView
        property int currentPkgOption:packageStackBridge.currentPkgOption
        Layout.fillHeight:true
        Layout.fillWidth:true
        Layout.alignment:Qt.AlignHCenter
        initialItem:pkgInfoView

        onCurrentPkgOptionChanged:{
            switch(currentPkgOption){
                case 0:
                    generalPkgView.replace(pkgInfoView)
                    break
                case 1:
                    generalPkgView.replace(pkgEulaView)
                    break
                case 2:
                    generalPkgView.replace(infoView)
                    break;
            }
        }

        replaceEnter: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 0
                to:1
                duration: 600
            }
        }
        replaceExit: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 1
                to:0
                duration: 600
            }
        }

        Component{
            id:pkgInfoView
            PackagesInfo{
               id:packagesInfo
            }
        }

        Component{
            id:pkgEulaView
            EulaPanel{
                id:eulaPanel
                eulaUrl:packageStackBridge.eulaUrl
            }
        }

        Component{
            id:infoView
            InfoPanel{
                id:infoPanel
            }
        }
    }
} 
