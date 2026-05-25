import QtQuick
import QtQuick.Controls
import QtQml.Models
import QtQuick.Layouts
import org.kde.plasma.components as PC

PC.ItemDelegate {
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
    property string metaInfo

    height: 65
    width: parent ? parent.width : 0
    enabled: true
          
    contentItem: Item {
        id: menuItem
    
        MouseArea {
            id: mouseAreaOption
            anchors.fill: parent
            hoverEnabled: true
            propagateComposedEvents: true
            
            onEntered: {
                listPkg.currentIndex = filterModel.visibleElements.indexOf(index)
            }
        } 

        RowLayout {
            anchors.fill:parent
            anchors.leftMargin: 5
            anchors.rightMargin: 5
            spacing: 10

            PC.CheckBox {
                id: packageCheck
                checked: listPkgItem.isChecked
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredWidth: visible ? implicitWidth : 0 
                visible: listPkgItem.showCb
                enabled: packageStackBridge.enablePkgList
                
                onToggled: {
                    packageStackBridge.onCheckPkg([listPkgItem.pkgId, checked])
                }
            }

            Image {
                id: packageIcon
                source: "image://iconProvider/" + listPkgItem.pkgIcon
                sourceSize.width: 32
                sourceSize.height: 32
                Layout.alignment: Qt.AlignVCenter
                cache: false
                mipmap: true
                smooth: true
                fillMode: Image.PreserveAspectFit
            } 

            Text {
                id: pkgName
                text: listPkgItem.order === 0 ? listPkgItem.customName : i18nd("epi-gtk", "Previous actions: executing ") + listPkgItem.customName
                Layout.fillWidth: true
                Layout.preferredWidth:0 
                elide: Text.ElideMiddle
                clip: true
                font.pointSize: 10
                Layout.alignment: Qt.AlignVCenter
            } 

            Image {
                id: resultImg
                source: listPkgItem.resultProcess === 0 ? "/usr/share/icons/breeze/status/24/data-success.svg" : "/usr/share/icons/breeze/status/24/data-error.svg"
                visible: listPkgItem.resultProcess !== -1
                sourceSize.width: 32
                sourceSize.height: 32
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredWidth: visible ? 32 : 0
                Layout.preferredHeight: visible ? 32 : 0
                cache: false
                mipmap: true
                smooth: true
                fillMode: Image.PreserveAspectFit
            }

            Rectangle {
                id: animationFrame
                color: "transparent"
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredWidth: visible ? 24 : 0
                Layout.preferredHeight: visible ? 24 : 0
                visible: packageCheck.checked && listPkgItem.showSpinner && mainStackBridge.isProcessRunning

                AnimatedImage {
                    id: animation
                    source: "/usr/lib/python3/dist-packages/epigtk/rsrc/loading.gif"
                    anchors.fill: parent
                    paused: !animationFrame.visible
                    fillMode: Image.PreserveAspectFit
                }
            }

            PC.Button {
                id: showInfoBtn
                display: AbstractButton.IconOnly
                icon.name: "help-about"
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredWidth: visible ? implicitWidth : 0
                
                visible: listPkgItem.ListView.isCurrentItem && 
                         !(listPkgItem.status === "installed" && listPkgItem.entryPoint !== "") && 
                         !mainStackBridge.isProcessRunning

                ToolTip {
                    id: showInfoToolTip
                    delay: 1000
                    timeout: 3000
                    visible: showInfoBtn.hovered
                    text: i18nd("epi-gtk", "Press to view application information")
                    background: Rectangle {
                        color: "#ffffff"
                        border.color: "#b8b9ba"
                        radius: 5.0
                    }
                }
                
                onClicked: {
                    packageStackBridge.showPkgInfo([0, listPkgItem.pkgId])
                }
            }

            PC.Button {
                id: entryPointBtn
                display: AbstractButton.IconOnly
                icon.name: "media-playback-playing"
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredWidth: visible ? implicitWidth : 0
                
                visible: listPkgItem.ListView.isCurrentItem && 
                         (listPkgItem.status === "installed" && listPkgItem.entryPoint !== "") && 
                         !mainStackBridge.isProcessRunning

                ToolTip {
                    id: entryPointToolTip
                    delay: 1000
                    timeout: 3000
                    visible: entryPointBtn.hovered
                    text: i18nd("epi-gtk", "Click to launch the application")
                    background: Rectangle {
                        color: "#ffffff"
                        border.color: "#b8b9ba"
                        radius: 5.0
                    }
                }
                
                onClicked: {
                    packageStackBridge.launchApp(listPkgItem.entryPoint)
                    mainWindow.close()
                }
            }
        }
    }
}
