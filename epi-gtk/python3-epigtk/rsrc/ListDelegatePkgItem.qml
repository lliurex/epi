import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.15
import QtQuick.Layouts 1.15
import org.kde.plasma.components 3.0 as PC3
import org.kde.plasma.core 2.0 as PlasmaCore // Importante para el icono nativo en QML 5

PC3.ItemDelegate {
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

    onHoveredChanged: {
        if (hovered){
            if (typeof listPkg !== "undefined" && typeof filterModel !== "undefined") {
                var targetIndex = filterModel.visibleElements.indexOf(index)
                if (targetIndex !== -1) {
                    listPkg.currentIndex = targetIndex
                }
            }
        }else{
            if (typeof listPkg !=="undefined" && listPkg.currentIndex===model.index){
                listPkg.currentIndex=-1
            }
        }
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

            AnimatedImage {
                id: animation
                source: "/usr/lib/python3/dist-packages/epigtk/rsrc/loading.gif"
                anchors.fill: parent
                paused: !animationFrame.visible
                fillMode: Image.PreserveAspectFit
            }
        }

        PC3.Button {
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

        PC3.Button {
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
