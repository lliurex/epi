import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.15
import QtQuick.Layouts 1.15
import org.kde.plasma.components 3.0 as PC3
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kirigami 2.16 as Kirigami

ItemDelegate {
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

    hoverEnabled: true
    leftPadding:15
    rightPadding:15

    background: Rectangle {
        anchors.fill: parent

        anchors.leftMargin: 5
        anchors.rightMargin: 5
        anchors.topMargin: 5
        anchors.bottomMargin: 0
    
        color: (listPkgItem.hovered || listPkgItem.ListView.isCurrentItem)
                ? Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.15)
                : "transparent"
                
        radius:6
        border.width:1
        border.color: (listPkgItem.hovered || listPkgItem.ListView.isCurrentItem)
                      ? Kirigami.Theme.highlightColor
                      : "transparent"
    }
    

    contentItem: RowLayout {
        id: mainRowLayout
        spacing: 10

        PC3.CheckBox {
            id: packageCheck
            checked: listPkgItem.isChecked
            Layout.alignment: Qt.AlignVCenter
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
            elide: Text.ElideMiddle
            clip: true
            font.pointSize: 10
            Layout.alignment: Qt.AlignVCenter
        }

        PlasmaCore.IconItem {
            id: resultImg
            source: listPkgItem.resultProcess === 0 ? "data-success" : "data-error"
            visible: listPkgItem.resultProcess !== -1
            Layout.preferredWidth: 32
            Layout.preferredHeight: 32
            Layout.alignment: Qt.AlignVCenter
        }

        Rectangle {
            id: animationFrame
            color: "transparent"
            Layout.alignment: Qt.AlignVCenter
            Layout.preferredWidth: visible ? 24 : 0
            Layout.preferredHeight: visible ? 24 : 0
            visible: packageCheck.checked && listPkgItem.showSpinner && mainStackBridge.isProcessRunning

            Image{
                id:spinnerImage
                source: "/usr/lib/python3/dist-packages/epigtk/rsrc/loading.png"
                anchors.fill:parent
                fillMode: Image.PreserveAspectFit
                smooth:true
                antialiasing:true

                rotation:0
            }
            Timer{
                id:rotationTimer
                running:animationFrame.visible
                repeat:true
                interval:60

                onTriggered:{
                    spinnerImage.rotation=(spinnerImage.rotation+10)%360

                }
            }
                
        }

        PC3.Button {
            id: showInfoBtn
            display: AbstractButton.IconOnly
            icon.name: "help-about"
            Layout.alignment: Qt.AlignVCenter
            Layout.preferredWidth: visible ? implicitWidth : 0

            visible: (listPkgItem.ListView.isCurrentItem || listPkgItem.hovered)&&
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

        PC3.Button {
            id: entryPointBtn
            display: AbstractButton.IconOnly
            icon.name: "media-playback-playing"
            Layout.alignment: Qt.AlignVCenter
            Layout.preferredWidth: visible ? implicitWidth : 0

            visible: (listPkgItem.ListView.isCurrentItem || listPkgItem.hovered)&&
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
