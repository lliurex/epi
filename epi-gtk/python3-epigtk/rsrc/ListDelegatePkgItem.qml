import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQml.Models 2.8
import org.kde.plasma.components 2.0 as Components
import org.kde.plasma.components 3.0 as PC3


Components.ListItem{

    id: listPkgItem
    property string pkgId
    property bool showCb
    property bool isChecked
    property string customName
    property string pkgIcon
    property string status
    property bool isVisible
    property int resultProcess
    property int order
    property bool showSpinner
    property string entryPoint

    enabled:true

    onContainsMouseChanged: {
         if (containsMouse) {
            let i=0
            do{
                listPkg.currentIndex=index-i
                i+=1

            }while (!listPkgItem.ListView.isCurrentItem)

        } else {
            listPkg.currentIndex = -1
        }
    }

    Item{
        id: menuItem
        height:visible?50:0
        width:parent.width-15

        PC3.CheckBox {
            id:packageCheck
            checked:isChecked
            onToggled:{
                console.log()
                epiBridge.onCheckPkg([pkgId,checked])
            }
            anchors.left:parent.left
            anchors.leftMargin:5
            anchors.verticalCenter:parent.verticalCenter
            visible:showCb
            enabled:epiBridge.enablePkgList
        }

        Image {
            id:packageIcon
            source:"image://iconProvider"+pkgIcon
            sourceSize.width:32
            sourceSize.height:32
            anchors.left:{
                if (showCb){
                    packageCheck.right
                }else{
                    parent.left
                }
            }
            anchors.verticalCenter:parent.verticalCenter
            anchors.leftMargin:10
            cache:false

        } 

        Text{
            id: pkgName
            text: {
                if (order==0){
                    customName
                }else{
                    i18nd("epi-gtk","Previous actions: executing ")+customName
                }
            }
            width: parent.width-150 
            elide:Text.ElideMiddle
            clip: true
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 10
            anchors.leftMargin:10
            anchors.left:packageIcon.right
            anchors.verticalCenter:parent.verticalCenter
        } 

        Image {
            id: resultImg
            source:{
                if (resultProcess==0){
                    "/usr/lib/python3/dist-packages/epigtk/rsrc/ok.png"
                }else{
                    "/usr/lib/python3/dist-packages/epigtk/rsrc/error.png"
                                 
                }
            }
            visible:{
                if (resultProcess!=-1){
                    true
                }else{
                    false
                }
            }
            sourceSize.width:32
            sourceSize.height:32
            anchors.leftMargin:10
            anchors.rightMargin:{
                if ((entryPointBtn.visible) || (showInfoBtn.visible)){
                    50
                }else{
                    1.5
                }
            }
            anchors.right:{
                if ((entryPointBtn.visible) || (showInfoBtn.visible)){
                    entryPoint.left
                }else{
                    parent.right
                }

            }
            anchors.verticalCenter:parent.verticalCenter
        }
        Rectangle{
            id:animationFrame
            color:"transparent"
            width:0.4*(animation.width)
            height:0.4*(animation.height)
            anchors.leftMargin:10
            anchors.right:parent.right
            anchors.verticalCenter:parent.verticalCenter
            visible:{
                if ((packageCheck.checked) && (showSpinner)){
                    epiBridge.isProcessRunning
                }else{
                    false
                }
            }

            AnimatedImage{
                id:animation
                source: "/usr/lib/python3/dist-packages/epigtk/rsrc/loading.gif"
                transform: Scale {xScale:0.40;yScale:0.40}
                paused:!animationFrame.visible
            }
        }

        PC3.Button{
            id:showInfoBtn
            display:AbstractButton.IconOnly
            icon.name:"help-about"
            anchors.leftMargin:10
            anchors.right:parent.right
            anchors.verticalCenter:parent.verticalCenter
            visible:{
                if (listPkgItem.ListView.isCurrentItem){
                    if ((status=="installed") && (entryPoint!="")){
                        false
                    }else{
                        if (!epiBridge.isProcessRunning){
                            true
                        }else{
                            false
                        }
                    }
                }else{
                    false
                }
            }
            ToolTip.delay: 1000
            ToolTip.timeout: 3000
            ToolTip.visible: hovered
            ToolTip.text:i18nd("epi-gtk","Press to view application information")
            onClicked:{
                epiBridge.showPkgInfo([0,pkgId])
            }
        }

        PC3.Button{
            id:entryPointBtn
            display:AbstractButton.IconOnly
            icon.name:"media-playback-playing"
            anchors.leftMargin:10
            anchors.right:parent.right
            anchors.verticalCenter:parent.verticalCenter
            visible:{
                if (listPkgItem.ListView.isCurrentItem){
                    if ((status=="installed") && (entryPoint!="")){
                        if (!epiBridge.isProcessRunning){
                            true
                        }else{
                            false
                        }
                    }else{
                        false
                    }
                }else{
                    false
                }
            }
            ToolTip.delay: 1000
            ToolTip.timeout: 3000
            ToolTip.visible: hovered
            ToolTip.text:i18nd("epi-gtk","Click to launch the application")
            onClicked:{
                epiBridge.launchApp(entryPoint)
                mainWindow.close()
            }
        }



    }

}
