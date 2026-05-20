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
                    return generalPkgView.replace(pkgInfoView)
                case 1:
                    return generalPkgView.replace(pkgEulaView)
                case 2:
                    return generalPkgView.replace(infoView)
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
