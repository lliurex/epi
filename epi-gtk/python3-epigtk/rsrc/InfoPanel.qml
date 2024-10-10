import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.plasma.components as PC


Rectangle{
    color:"transparent"
    Text{ 
        text:i18nd("epi-gtk","Additional information")
        font.family: "Quattrocento Sans Bold"
        font.pointSize: 16
    }

    GridLayout{
        id:infoLayout
        rows:2
        flow: GridLayout.TopToBottom
        rowSpacing:10
        width:parent.width-10
        height:parent.height-25
        anchors.left:parent.left

        RowLayout{
            spacing:10
            Layout.topMargin:40
            Layout.bottomMargin:10
            Layout.fillWidth:true

            Image{
                id:pkgIcon
                source:packageStackBridge.pkgStoreInfo[0]
                sourceSize.width:64
                sourceSize.height:64
                Layout.alignment:Qt.AlignVCenter
            }
            ColumnLayout{
                spacing:5
                Layout.fillWidth:true
                Layout.alignment:Qt.AlignVCenter
                Text{
                    id:pkgNameText
                    text:packageStackBridge.pkgStoreInfo[1]
                    visible:true
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 14
                    horizontalAlignment:Text.AlignLeft
                    Layout.preferredWidth:200
                    Layout.fillWidth:true
                }
                Text{
                    id:pkgSummayText
                    text:packageStackBridge.pkgStoreInfo[2]
                    visible:true
                    font.family: "Quattrocento Sans"
                    font.pointSize: 12
                    horizontalAlignment:Text.AlignLeft
                    Layout.preferredWidth:200
                    Layout.fillWidth:true
                    wrapMode: Text.WordWrap
                }
            }
       }

       RowLayout{
           Rectangle{
               id:container
               color:"transparent"
               width:parent.width
               height:parent.height
               clip:true

               PC.ScrollView{
                   implicitWidth:parent.width
                   implicitHeight:parent.height
                   anchors.leftMargin:11
                   Text{
                       id:pkgDescriptionText
                       text:packageStackBridge.pkgStoreInfo[3]
                       font.family: "Quattrocento Sans"
                       font.pointSize: 11
                       horizontalAlignment:Text.AlignLeft
                       width:container.width
                       height:container.height
                       wrapMode: Text.WordWrap
                   }
               }
                
           }
        }
    }

} 
