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
    property bool isRunning
    property int resultProcess
    property int order

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
                console.log(pkgId)
            }
            anchors.left:parent.left
            anchors.leftMargin:5
            anchors.verticalCenter:parent.verticalCenter
            visible:showCb
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
            cache:false

        } 

        Text{
            id: pkgName
            text: customName
            width: parent.width-150 
            elide:Text.ElideMiddle
            clip: true
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 11
            anchors.leftMargin:5
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
            anchors.leftMargin:5
            anchors.left:pkgName.right
            anchors.verticalCenter:parent.verticalCenter
        }
        Rectangle{
            color:"transparent"
            width:30
            height:30
            anchors.leftMargin:5
            anchors.left:resultImg.right
            anchors.verticalCenter:parent.verticalCenter
            visible:isRunning

            AnimatedImage{
                source: "/usr/lib/python3/dist-packages/epigtk/rsrc/loading.gif"
                transform: Scale {xScale:0.40;yScale:0.40}
              }
        }

    }

}
