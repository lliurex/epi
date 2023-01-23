import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQml.Models 2.8
import org.kde.plasma.components 2.0 as Components
import org.kde.plasma.components 3.0 as PC3
import org.kde.kirigami 2.12 as Kirigami
import QtQuick.Layouts 1.12


Rectangle{
    property alias packagesModel:filterModel.model
    property alias listCount:listPkg.count
    id: optionsGrid
    color:"transparent"

    GridLayout{
        id:mainGrid
        rows:2
        flow: GridLayout.TopToBottom
        rowSpacing:10
        anchors.left:parent.left
        anchors.fill:parent

        TextField{
            id:pkgSearchEntry
            font.pointSize:10
            horizontalAlignment:TextInput.AlignLeft
            Layout.alignment:Qt.AlignRight
            Layout.topMargin:40
            focus:true
            width:200
            placeholderText:i18nd("epi-gtk","Search")
            onTextChanged:{
                filterModel.update()
            }
        }

        Rectangle {
            id:pkgTable
            visible: true
            color:"white"
            Layout.fillHeight:true
            Layout.fillWidth:true
            border.color: "#d3d3d3"

            PC3.ScrollView{
                implicitWidth:parent.width
                implicitHeight:parent.height
                anchors.leftMargin:10
       
                ListView{
                    id: listPkg
                    property int totalItems
                    anchors.fill:parent
                    height: parent.height
                    enabled:true
                    currentIndex:-1
                    clip: true
                    focus:true
                    boundsBehavior: Flickable.StopAtBounds
                    highlight: Rectangle { color: "#add8e6"; opacity:0.8;border.color:"#53a1c9" }
                    highlightMoveDuration: 0
                    highlightResizeDuration: 0
                    model:FilterDelegateModel{
                        id:filterModel
                        model:packagesModel
                        role:"customName"
                        search:pkgSearchEntry.text.trim()
                        delegate: ListDelegatePkgItem{
                            width:pkgTable.width
                            pkgId:model.pkgId
                            showCb:model.showCb
                            isChecked:model.isChecked
                            customName:model.customName
                            pkgIcon:model.pkgIcon
                            status:model.status
                            isVisible:model.isVisible
                            isRunning:model.isRunning
                            resultProcess:model.resultProcess
                            order:model.order
                        }
                    }

                    Kirigami.PlaceholderMessage { 
                        id: emptyHint
                        anchors.centerIn: parent
                        width: parent.width - (units.largeSpacing * 4)
                        visible: listCount.count==0?true:false
                        text: "No pacakges"
                    }

                 } 
            }
        }
    }

}

