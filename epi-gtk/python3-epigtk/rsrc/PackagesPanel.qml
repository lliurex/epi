import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


RowLayout{
    id:generalPkgLayout
    spacing: 10
    Layout.fillWidth: true
    Layout.fillHeight: true
 
    StackView{
        id:generalPkgView
        property int currentPkgOption:packageStackBridge.currentPkgOption
        Layout.fillHeight:true
        Layout.fillWidth:true
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
                    break
            }
        }

        replaceEnter: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 0
                to:1
                duration: 60
            }
        }
        replaceExit: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 1
                to:0
                duration: 60
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
